import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient
import datetime

# Calculates derivation of room temp and increases/lowers target temp. accordingly
# (kind of adding a D part to a PI controller)
#
# Args:
# - db_passwd
# - db_measurement
# - db_field
# - multiplicator => e.g. derivative of -0.1 K/h should lead to shift of +0.5K => 5
# - limit_max
# - limi_min

class heating_controller_foresight(hass.Hass):

    def initialize(self):
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        
        self.db_measurement: Set[str] = self.args.get("db_measurement", set())
        self.db_field: Set[str] = self.args.get("db_field", set())
        
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=0, second=40))
        self.calc_derivation_hourly(None)
    
    def calc_derivation(self, kwargs):
        current_value = float(self.get_state("sensor.temp_esszimmer_taster"))
        for hour in range(1,9):
            query = 'SELECT last("state_float") FROM "homeassistant_permanent"."autogen"."sensor.temp_esszimmer_taster" WHERE time > now() - 24h AND time < now() - {}h'.format(hour)
            #self.log(query)
            result_points = self.client.query(query).get_points()
            #self.log(historic_value)
            for point in result_points:
                historic_value = point["last"]
                derivative = (current_value - historic_value) / hour
                #self.log(derivative)
                break
            self.log("hour: {} / historic_value: {:.1f} / derivative: {:.4f}".format(hour, round(historic_value,1), round(derivative,4)))

    def calc_derivation_hourly(self, kwargs):
        current_value = float(self.get_state("sensor.temp_esszimmer_taster"))
        der_list = []
        for hour in range(1,9):
            query = 'SELECT last("state_float") FROM "homeassistant_permanent"."autogen"."sensor.temp_esszimmer_taster" WHERE time > now() - 24h AND time < now() - {}h'.format(hour)
            #self.log(query)
            result_points = self.client.query(query).get_points()
            #self.log(historic_value)
            for point in result_points:
                historic_value = point["last"]
                derivative = (current_value - historic_value) / hour
                der_list.append(derivative)
                #self.log(derivative)
                break
        self.log(' // '.join('{}: {:.4f}'.format(*k) for k in enumerate(der_list, start=1)))
        mean_derivative_1 = der_list[0] # 1
        mean_derivative_12 = (der_list[0] + der_list[1])/2 # mean of 1, 2 hours
        mean_derivative_123 = (der_list[0] + der_list[1] + der_list[2])/3 # mean of 1, 2 and 3 hours
        mean_derivative_246 = (der_list[1] + der_list[3] + der_list[5])/3 # mean of 1, 2 and 3 hours
        shift_kelvin_1 = (- mean_derivative_1) * self.args.get("multiplicator", 0)
        shift_kelvin_12 = (- mean_derivative_12) * self.args.get("multiplicator", 0)
        shift_kelvin_123 = (- mean_derivative_123) * self.args.get("multiplicator", 0)
        shift_kelvin_246 = (- mean_derivative_246) * self.args.get("multiplicator", 0)
        self.log("Calculated Offset: {:.2f} / {:.2f} / {:.2f} / {:.2f} K".format(shift_kelvin_1, shift_kelvin_12, shift_kelvin_123, shift_kelvin_246))
        self.client.write_points([{"measurement":"test_heating_controller_ez","fields":{"shift_kelvin_1":shift_kelvin_1, "shift_kelvin_12":shift_kelvin_12, "shift_kelvin_123":shift_kelvin_123, "shift_kelvin_246":shift_kelvin_246}}])
