import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient
import datetime
import random

# Calculates derivation of room temp and increases/lowers target temp. accordingly
# (kind of adding a D part to a PI controller)
#
# Args:
# - db_passwd
# - db_measurement
# - db_field
# - multiplicator => e.g. derivative of -0.1 K/h should lead to shift of +0.5K => 5
# - limit_max
# - limit_min
# - ga_setpoint_shift (ga for 1byte shift of setpoint)
# - shift_value (optional, default: 0.1)
# - mode (active or log)
# - on_off_switch: input_boolean.korrektur_heizung_ez
# - log_measurement => test_heating_controller_ez

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
        
        random_second = random.randint(0,59)
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=0, second=random_second))
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=10, second=random_second))
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=20, second=random_second))
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=30, second=random_second))
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=40, second=random_second))
        self.run_hourly(self.calc_derivation_hourly, datetime.time(hour=0, minute=50, second=random_second))
        self.calc_derivation_hourly(None)
        self.beta(None)
        
        self.listen_state(self.on_off_switch, self.args["on_off_switch"])
    

    def calc_derivation_hourly(self, kwargs):
        try:
            current_value = float(self.get_state(self.db_measurement))
        except:
            self.log("Error converting State of {} to float".format(self.db_measurement))
            return
        der_list = []
        for minutes in range(30,240,30):
            query = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time > now() - 24h AND time < now() - {}m'.format(self.db_field, self.db_measurement, minutes)
            #self.log(query)
            result_points = self.client.query(query).get_points()
            #self.log(historic_value)
            for point in result_points:
                historic_value = point["last"]
                derivative = (current_value - historic_value) / (minutes / 60)
                der_list.append(derivative)
                #self.log(derivative)
                break
        self.log(' // '.join('{}: {:.4f}'.format(*k) for k in enumerate(der_list, start=1)))
        mean_derivative_30 = der_list[0]
        mean_derivative_60 = der_list[1]
        mean_derivative_90 = der_list[2]
        mean_derivative_120 = der_list[3]
        mean_derivative_3060 = (der_list[0] + der_list[1])/2
        mean_derivative_306090 = (der_list[0] + der_list[1] + der_list[2])/3
        mean_derivative_306090120 = (der_list[0] + der_list[1] + der_list[2] + der_list[3])/4
        mean_derivative_60120 = (der_list[1] + der_list[3])/2
        mean_derivative_60120180 = (der_list[1] + der_list[3] + der_list[5])/3
        shift_kelvin_30 = (- mean_derivative_30) * self.args.get("multiplicator", 0)
        shift_kelvin_60 = (- mean_derivative_60) * self.args.get("multiplicator", 0)
        shift_kelvin_90 = (- mean_derivative_90) * self.args.get("multiplicator", 0)
        shift_kelvin_120 = (- mean_derivative_120) * self.args.get("multiplicator", 0)
        shift_kelvin_3060 = (- mean_derivative_3060) * self.args.get("multiplicator", 0)
        shift_kelvin_306090 = (- mean_derivative_306090) * self.args.get("multiplicator", 0)
        shift_kelvin_306090120 = (- mean_derivative_306090120) * self.args.get("multiplicator", 0)
        shift_kelvin_60120 = (- mean_derivative_60120) * self.args.get("multiplicator", 0)
        shift_kelvin_60120180 = (- mean_derivative_60120180) * self.args.get("multiplicator", 0)
        self.log("Calculated Offset: {:.2f} / {:.2f} / {:.2f} / {:.2f} K".format(shift_kelvin_30, shift_kelvin_60, shift_kelvin_60, shift_kelvin_120))
        self.client.write_points([{"measurement":self.args.get("log_measurement", "test_no_name"),"fields":{"shift_kelvin_30":shift_kelvin_30, "shift_kelvin_60":shift_kelvin_60, "shift_kelvin_90":shift_kelvin_90, "shift_kelvin_120":shift_kelvin_120, "shift_kelvin_3060":shift_kelvin_3060, "shift_kelvin_306090":shift_kelvin_306090, "shift_kelvin_306090120":shift_kelvin_306090120, "shift_kelvin_60120":shift_kelvin_60120, "shift_kelvin_30120180":shift_kelvin_60120180}}])
       
           
        shift_kelvin = shift_kelvin_306090
        self.log("Shift Kelvin: {}".format(shift_kelvin))
        if shift_kelvin > self.args.get("limit_max", 1):
            shift_kelvin = self.args.get("limit_max", 1)
        if shift_kelvin < self.args.get("limit_min", -1):
            shift_kelvin = self.args.get("limit_min", -1)
        
        shift_value = self.args.get("shift_value", 0.1)
        shift_points = round(shift_kelvin / shift_value)
        self.log("Shift-Points: {}".format(shift_points))
        if shift_points > 0:
            value_byte = shift_points
        elif shift_points < 0:
            value_byte = 256 + shift_points
        else:
            value_byte = 0
        #self.log("Value byte: {}".format(value_byte))
        
        if self.args.get("mode", "log") == "active" and self.get_state(self.args["on_off_switch"]) == "on":
            self.log("Will send {} to ga {} now".format(value_byte,self.args.get("ga_setpoint_shift")))
            self.call_service("knx/send", address = self.args.get("ga_setpoint_shift"), payload = [value_byte])

    def beta(self, kwargs):
        der_list = []
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time > now() - 24h ORDER BY time DESC LIMIT 5'.format(self.db_field, self.db_measurement)
        #self.log(query)
        result_points = self.client.query(query).get_points()
        prev_value = None
        prev_time = None
        for point in result_points:
            self.log(point)
            #self.log(type(point["time"]))
            if prev_value != None:
                delta_value = point[self.db_field] - prev_value
                delta_time = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%f') - prev_time
                delta_time_seconds = delta_time.total_seconds()
                derivative = delta_value / (delta_time_seconds / 3600)
                der_list.append(derivative)
                self.log(derivative)
            prev_value = point[self.db_field]
            prev_time = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%f')

    
    def on_off_switch(self, entity, attribute, old, new, kwargs):
        if new == "off" and old != new:
            self.call_service("knx/send", address = self.args.get("ga_setpoint_shift"), payload = [0])
            self.log("Reset Setpoint Shift to 0")
