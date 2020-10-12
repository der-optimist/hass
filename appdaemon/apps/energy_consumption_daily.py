import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient
import datetime
#from statistics import median

# Calculate Energy consumption from power data and write it to influxdb
#
# Args:
# - db_passwd
# - db_measurement
# - db_field


class energy_consumption_daily(hass.Hass):

    def initialize(self):
        # define daily time to run the calculation:
        daily_time =  datetime.time(4, 35, 43)
        #daily_time =  datetime.time(9, 14, 0)
        # initialize database stuff
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        self.db_measurements_Watt = self.args["db_measurements_Watt"]
        self.db_measurements_kWh = self.args["db_measurements_kWh"]
        self.db_field: Set[str] = self.args.get("db_field", set())
        self.price_per_kWh = self.args.get("price_per_kWh", 0.0)
        self.save_measurement_name = self.args.get("save_measurement_name", "energy_consumption_test")
        special_date = self.args.get("special_date", None)
        # calculate for a given single date
        if special_date is not None:
            self.calculate_energy_consumption(special_date)
        # run daily
        self.run_daily(self.generate_data_for_yesterday, daily_time)
        # drop some measurements from testing
        #self.drop()
        
        
    def generate_data_for_yesterday(self, kwargs):
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        self.log("running consumption calclulation for " + yesterday_str)
        consumption_total, cost_total, details_dict = self.calculate_energy_consumption(yesterday_str)
        message_text = "Verbrauch gestern: {} kWh => {} €\n\nVerbrauch im Detail:".format(round(consumption_total,1),round(cost_total,2))
        details_sorted = sorted(details_dict.items(), key=lambda x: x[1], reverse=True)
        for i in details_sorted:
            message_text = message_text + "\n{}: {} kWh => {} €".format(i[0],round(i[1],1),round(i[1]*self.price_per_kWh,2))
        self.fire_event("custom_notify", message=message_text, target="telegram_jo")
        

    def calculate_energy_consumption(self, date_str):
        known_consumption_kWh_total = 0
        details_dict = dict()
        ts_start_local = datetime.datetime.strptime(date_str + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_start_local_ns = ts_start_local  * 1e9
        ts_start_local_ns_plus_buffer = ts_start_local_ns - 12*3600*1e9 # +12 hours for query to know value before that day started
        ts_end_local = datetime.datetime.strptime(date_str + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_end_local_ns = ts_end_local * 1e9 + 999
        ts_save_local_ns = datetime.datetime.strptime(date_str + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        utc_offset_timestamp = datetime.datetime.now().timestamp() - datetime.datetime.utcnow().timestamp()
        # calculate from power logs in Watt
        for measurement in self.db_measurements_Watt.keys():
            if measurement.startswith("sensor."):
                sensor_name = measurement.split("sensor.")[1]
            else:
                sensor_name = measurement
            query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, measurement, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
            #self.log(query)
            result_points = self.client.query(query).get_points()
            consumption_Ws = 0.0
            past_timestep = ts_end_local
            start_time_reached = False
            for point in result_points:
                #self.log(point)
                timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
                #self.log("timestamp local: {}".format(timestamp_local))
                if timestamp_local < ts_start_local:
                    timestamp_local = ts_start_local
                    start_time_reached = True
                time_delta_s = past_timestep - timestamp_local
                #self.log("timedelta: {} s".format(time_delta_s))
                energy_Ws = point[self.db_field] * time_delta_s
                #self.log("energy: {} Ws".format(energy_Ws))
                consumption_Ws = consumption_Ws + energy_Ws
                past_timestep = timestamp_local
                if start_time_reached:
                    break
            consumption_kWh = consumption_Ws / 3600000
            cost = consumption_kWh * self.price_per_kWh
            self.log("Verbrauch {}: {} kWh, also {} EUR (berechnet aus Leistung)".format(sensor_name, round(consumption_kWh,2),round(cost,2)))
            # save to db
            self.client.write_points([{"measurement":self.save_measurement_name,"fields":{sensor_name:consumption_kWh},"time":int(ts_save_local_ns)}])
            details_dict[self.db_measurements_Watt.get(measurement,sensor_name)] = consumption_kWh
            known_consumption_kWh_total = known_consumption_kWh_total + consumption_kWh
        # calculate from consumption logs in kWh:
        for measurement in self.db_measurements_kWh.keys():
            if measurement.startswith("sensor."):
                sensor_name = measurement.split("sensor.")[1]
            else:
                sensor_name = measurement
            query_start = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_start_local_ns))
            counter_start_generator = result_points = self.client.query(query_start).get_points()
            for point in counter_start_generator:
                counter_start = point["last"]
            query_end = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_end_local_ns))
            counter_end_generator = result_points = self.client.query(query_end).get_points()
            for point in counter_end_generator:
                counter_end = point["last"]
            consumption_kWh = counter_end - counter_start
            cost = consumption_kWh * self.price_per_kWh
            self.log("Verbrauch {}: {} kWh, also {} EUR (berechnet aus Zaehlerstand)".format(sensor_name, round(consumption_kWh,2),round(cost,2)))
            # save to db
            self.client.write_points([{"measurement":self.save_measurement_name,"fields":{sensor_name:consumption_kWh},"time":int(ts_save_local_ns)}])
            details_dict[self.db_measurements_kWh.get(measurement,sensor_name)] = consumption_kWh
            known_consumption_kWh_total = known_consumption_kWh_total + consumption_kWh
        known_consumption_costs = known_consumption_kWh_total  * self.price_per_kWh
        self.log("Stromverbrauch von bekannten Dingen, {}: {} kWh, also {} EUR ".format(date_str, round(known_consumption_kWh_total,1),round(known_consumption_costs,2)))
        return known_consumption_kWh_total, known_consumption_costs, details_dict
            


    
    def drop(self):
        self.client.drop_measurement("test_heating_controller_ez")