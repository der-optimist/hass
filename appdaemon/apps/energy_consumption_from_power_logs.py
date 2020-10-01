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


class energy_consumption_from_power_logs(hass.Hass):

    def initialize(self):
        # initialize database stuff
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        self.db_measurement: Set[str] = self.args.get("db_measurement", set())
        self.db_field: Set[str] = self.args.get("db_field", set())
        
        self.date = "2020-09-30"
        
        self.calculate_energy_consumption(None)
        
        # drop some measurements from testing
        #self.drop()

    def calculate_energy_consumption(self, kwargs):
        ts_start_local = datetime.datetime.strptime(self.date + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_start_local_ns = ts_start_local  * 1e9
        ts_start_local_ns_plus_buffer = ts_start_local_ns - 12*3600*1e9 # +12 hours for query to know value before that day started
        ts_end_local = datetime.datetime.strptime(self.date + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_end_local_ns = ts_end_local * 1e9 + 999
        utc_offset_timestamp = datetime.datetime.now().timestamp() - datetime.datetime.utcnow().timestamp()
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_measurement, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
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
        self.log("Verbrauch: {} Ws bzw. {} kWh".format(consumption_Ws, consumption_kWh))
        # save to db
        ts_save_local_ns = datetime.datetime.strptime(self.date + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        self.client.write_points([{"measurement":"energy_consumption_test","fields":{"lueftungsanlage":consumption_kWh},"time":int(ts_save_local_ns)}])
#            if newest_value == None:
#                newest_value = point[self.db_field]
#                current_time = datetime.datetime.utcnow()
                #self.log(current_time.strftime("%Y-%m-%d %H:%M:%S"))
#            else:
#                delta_value = point[self.db_field] - newest_value
#                delta_time = datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f') - current_time
                #self.log(datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S"))
#                delta_time_seconds = delta_time.total_seconds()
#                derivative = delta_value / (delta_time_seconds / 3600)
#                der_list.append(derivative)

            


    
    def drop(self):
        self.client.drop_measurement("test_heating_controller_ez")
