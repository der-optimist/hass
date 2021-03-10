import appdaemon.plugins.hass.hassapi as hass
import datetime

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
        self.listen_state(self.sensor_rest_forecast_changed, self.sensor_rest_forecast, attribute = "forecasts")
        try:
            current_forecasts = self.get_state(self.sensor_rest_forecast, attribute = "forecasts")
            self.sensor_rest_forecast_changed(self.sensor_rest_forecast, "forecasts", None, current_forecasts, None)
        except Exception as e:
            self.log("Error running forecast at startup. Error was {}".format(e))
 
    def sensor_rest_forecast_changed(self, entity, attribute, old, new, kwargs):
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
#        start_dt = (datetime.datetime.now() - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
#        end_dt = (datetime.datetime.now() + datetime.timedelta(days=self.days_birthdays) - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url


    def check_reminder(self, kwargs):
        pass

        
    def utc_offset(self, kwargs):
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
        #self.log("utc offset: {}d {}sec".format(utc_offset_dt.days, utc_offset_dt.seconds))
        return utc_offset_dt
