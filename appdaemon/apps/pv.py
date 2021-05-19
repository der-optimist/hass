import appdaemon.plugins.hass.hassapi as hass
import datetime
from influxdb import InfluxDBClient

#
# What it does:
#   - 
# What args it needs:
#   - 
#  

class pv(hass.Hass):

    def initialize(self):
        # --- forecast ---
        self.sensor_rest_forecast = "sensor.solcast_forecast_rest"
        self.sensor_forecast_data_chart = "sensor.solcast_forecast_chart"
        self.listen_state(self.update_forecast, self.sensor_rest_forecast, attribute = "forecasts")
#        try:
#            current_forecasts = self.get_state(self.sensor_rest_forecast, attribute = "forecasts")
#            self.update_forecast(self.sensor_rest_forecast, "forecasts", None, current_forecasts, None)
#        except Exception as e:
#            self.log("Error running forecast at startup. Error was {}".format(e))
        self.run_every(self.update_forecast_regularly, "now", 15 * 60)
        # --- initialize database stuff
        self.host = self.app_config["global_vars"]["db_host"]
        self.port = self.app_config["global_vars"]["db_port"]
        self.user = self.app_config["global_vars"]["db_user"]
        self.password = self.app_config["global_vars"]["db_passwd"]
        self.db_name = self.app_config["global_vars"]["db_name"]
        self.db_field_float = self.app_config["global_vars"]["db_field_float"]
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.db_name)
        # --- values of today ---
        self.ad_namespace = self.app_config["global_vars"]["ad_namespace"]
        self.run_daily(self.save_counter_values_at_midnight, datetime.time(23, 59, 30))
        #self.save_counter_values_at_midnight(None)
        self.run_every(self.update_daily_counters, "now+10", 5 * 60)
        
    
    def save_counter_values_at_midnight(self, kwargs):
        # calculate production of the day
        pv_produced_day = float(self.get_state(self.args["counter_entity_pv_produced"])) - float(self.get_state(self.args["sensor_name_counter_pv_produced_midnight"], namespace = self.ad_namespace))
        pv_sold_day = float(self.get_state(self.args["counter_entity_pv_sold"])) - float(self.get_state(self.args["sensor_name_counter_pv_sold_midnight"], namespace = self.ad_namespace))
        # reset counters fo next day
        value_counter_pv_produced_midnight = self.get_state(self.args["counter_entity_pv_produced"])
        self.set_state(self.args["sensor_name_counter_pv_produced_midnight"], state = value_counter_pv_produced_midnight, attributes = {"updated":datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}, namespace = self.ad_namespace)
        value_counter_pv_sold_midnight = self.get_state(self.args["counter_entity_pv_sold"])
        self.set_state(self.args["sensor_name_counter_pv_sold_midnight"], state = value_counter_pv_sold_midnight, attributes = {"updated":datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}, namespace = self.ad_namespace)
        # save to db
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        ts_save_local_ns = datetime.datetime.strptime(date_str + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        self.client.write_points([{"measurement":self.args["counter_entity_pv_produced_day"],"fields":{self.db_field_float:pv_produced_day},"time":int(ts_save_local_ns)}])
        self.client.write_points([{"measurement":self.args["counter_entity_pv_sold_day"],"fields":{self.db_field_float:pv_sold_day},"time":int(ts_save_local_ns)}])
        self.client.write_points([{"measurement":self.args["counter_entity_pv_used_day"],"fields":{self.db_field_float:(pv_produced_day - pv_sold_day)},"time":int(ts_save_local_ns)}])
        saved_money_by_selling_day = pv_sold_day * self.get_state(self.app_config["global_vars"]["input_number_entity_compensation_per_kwh"])
        self.client.write_points([{"measurement":self.args["entity_pv_saved_money_by_selling_day"],"fields":{self.db_field_float:saved_money_by_selling_day},"time":int(ts_save_local_ns)}])
        saved_money_by_consuming_day = (pv_produced_day - pv_sold_day) * self.get_state(self.app_config["global_vars"]["input_number_entity_price_per_kwh"])
        self.client.write_points([{"measurement":self.args["entity_pv_saved_money_by_consuming_day"],"fields":{self.db_field_float:saved_money_by_consuming_day},"time":int(ts_save_local_ns)}])
        self.client.write_points([{"measurement":self.args["entity_pv_saved_money_total_day"],"fields":{self.db_field_float:(saved_money_by_selling_day + saved_money_by_consuming_day)},"time":int(ts_save_local_ns)}])
        
    def update_daily_counters(self, kwargs):
        pv_produced_day = float(self.get_state(self.args["counter_entity_pv_produced"])) - float(self.get_state(self.args["sensor_name_counter_pv_produced_midnight"], namespace = self.ad_namespace))
        pv_sold_day = float(self.get_state(self.args["counter_entity_pv_sold"])) - float(self.get_state(self.args["sensor_name_counter_pv_sold_midnight"], namespace = self.ad_namespace))
        self.set_state(self.args["counter_entity_pv_produced_day"], state = round(pv_produced_day,1), attributes = {"fiendly_name": "PV-Erzeugung heute", "icon":"mdi:counter",  "unit_of_measurement": "kWh"})
        self.set_state(self.args["counter_entity_pv_sold_day"], state = round(pv_sold_day,1), attributes = {"fiendly_name": "PV-Einspeisung heute", "icon":"mdi:counter",  "unit_of_measurement": "kWh"})
        
    def update_forecast_regularly(self, kwargs):
        current_forecasts = self.get_state(self.sensor_rest_forecast, attribute = "forecasts")
        self.update_forecast(self.sensor_rest_forecast, "forecasts", None, current_forecasts, None)
 
    def update_forecast(self, entity, attribute, old, new, kwargs):
        self.log("updating solar forecast - start")
        timestamps = []
        forecast_values = []
        timestamps_daily = []
        forecast_values_daily = []
        utc_offset = self.utc_offset(None)
        day_0 = datetime.datetime.now().date()
        day_1 = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        day_2 = (datetime.datetime.now() + datetime.timedelta(days=2)).date()
        day_3 = (datetime.datetime.now() + datetime.timedelta(days=3)).date()
        day_4 = (datetime.datetime.now() + datetime.timedelta(days=4)).date()
        day_5 = (datetime.datetime.now() + datetime.timedelta(days=5)).date()
        energy_day_0 = 0
        energy_day_1 = 0
        energy_day_2 = 0
        energy_day_3 = 0
        energy_day_4 = 0
        energy_day_5 = 0
        for forecast in new:
            end_time_string = forecast["period_end"][:26]
            mid_time = datetime.datetime.strptime(end_time_string, "%Y-%m-%dT%H:%M:%S.%f") - datetime.timedelta(minutes=15)
            mid_time_string = datetime.datetime.strftime(mid_time,"%Y-%m-%dT%H:%M:%S.%f") + "Z"
            value_watt = int(round(float(forecast["pv_estimate"]) * 1000,0))
            timestamps.append(mid_time_string)
            forecast_values.append(value_watt)
            mid_time_local = mid_time + utc_offset
            mid_time_local_day = mid_time_local.date()
            if mid_time_local_day == day_0:
                if mid_time_local > datetime.datetime.now():
                    energy_day_0 += (value_watt * 0.5) / 1000
            elif mid_time_local_day == day_1:
                energy_day_1 += (value_watt * 0.5) / 1000
            elif mid_time_local_day == day_2:
                energy_day_2 += (value_watt * 0.5) / 1000
            elif mid_time_local_day == day_3:
                energy_day_3 += (value_watt * 0.5) / 1000
            elif mid_time_local_day == day_4:
                energy_day_4 += (value_watt * 0.5) / 1000
            elif mid_time_local_day == day_5:
                energy_day_5 += (value_watt * 0.5) / 1000
        timestamps_daily.append(datetime.datetime.combine(day_0, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        timestamps_daily.append(datetime.datetime.combine(day_1, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        timestamps_daily.append(datetime.datetime.combine(day_2, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        timestamps_daily.append(datetime.datetime.combine(day_3, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        timestamps_daily.append(datetime.datetime.combine(day_4, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        timestamps_daily.append(datetime.datetime.combine(day_5, datetime.time(0,0,0,0)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
        forecast_values_daily.append(round(energy_day_0,1))
        forecast_values_daily.append(round(energy_day_1,1))
        forecast_values_daily.append(round(energy_day_2,1))
        forecast_values_daily.append(round(energy_day_3,1))
        forecast_values_daily.append(round(energy_day_4,1))
        forecast_values_daily.append(round(energy_day_5,1))
        self.set_state(self.sensor_forecast_data_chart, state = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")), attributes = {"timestamps": timestamps, "forecast_values": forecast_values, "timestamps_daily": timestamps_daily, "forecast_values_daily": forecast_values_daily})
        self.log("updating solar forecast - done")


    def check_reminder(self, kwargs):
        pass

        
    def utc_offset(self, kwargs):
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
        #self.log("utc offset: {}d {}sec".format(utc_offset_dt.days, utc_offset_dt.seconds))
        return utc_offset_dt
