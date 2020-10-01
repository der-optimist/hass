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
        ts_start = datetime.datetime.strptime(self.date + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        ts_end = datetime.datetime.strptime(self.date + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9 + 999
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_measurement, int(ts_start), (ts_end))
        self.log(query)
        result_points = self.client.query(query).get_points()
        self.log(result_points)
        return
        newest_value = None
        current_time = None
        for point in result_points:
            self.log(point)
            if newest_value == None:
                newest_value = point[self.db_field]
                current_time = datetime.datetime.utcnow()
                #self.log(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                delta_value = point[self.db_field] - newest_value
                delta_time = datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f') - current_time
                #self.log(datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S"))
                delta_time_seconds = delta_time.total_seconds()
                derivative = delta_value / (delta_time_seconds / 3600)
                der_list.append(derivative)

            


    
    def drop(self):
        self.client.drop_measurement("test_heating_controller_ez")
