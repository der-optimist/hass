import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient
import datetime
import random
from statistics import median

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
        # initialize database stuff
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        self.db_measurement: Set[str] = self.args.get("db_measurement", set())
        self.db_field: Set[str] = self.args.get("db_field", set())
        
        self.minutes_for_evaltuation = self.args.get("minutes_for_evaltuation", [60, 90, 120, 150, 180])
        
        # run every 5 minutes, but at random start time
        random_second = random.randint(0,59)
        random_minute = random.randint(0,4)
        for minute in range(random_minute,random_minute+56,5):
            self.run_hourly(self.shift_controller_setpoint, datetime.time(hour=0, minute=minute, second=random_second))
        # especially when testing, also start immediately
        self.shift_controller_setpoint(None)
        
        # reset shift to 0 when switching off this app
        self.listen_state(self.on_off_switch, self.args["on_off_switch"])
        
        # drop some measurements from testing
        #self.drop()

    def shift_controller_setpoint(self, kwargs):
        der_list = self.get_list_of_derivatives()
        # use median. Intention was, that a peak in the measurement should not change the result too much, as it would be the case with average
        median_of_derivatives = median(der_list)
        shift_kelvin = (- median_of_derivatives) * self.args.get("multiplicator", 0)
        
        # limit the shifting of the setpint, so that this app can't spoil too much :-)
        if shift_kelvin > self.args.get("limit_max", 1):
            shift_kelvin_limited = self.args.get("limit_max", 1)
        elif shift_kelvin < self.args.get("limit_min", -1):
            shift_kelvin_limited = self.args.get("limit_min", -1)
        else:
            shift_kelvin_limited = shift_kelvin
        
        # calulate byte value from shift_kelvin
        value_byte = self.shift_kelvin_to_byte_value(shift_kelvin_limited)
        
        if self.args.get("mode", "log") == "active" and self.get_state(self.args["on_off_switch"]) == "on":
            #self.log("Will send {} to ga {} now".format(value_byte,self.args.get("ga_setpoint_shift")))
            self.call_service("knx/send", address = self.args.get("ga_setpoint_shift"), payload = [value_byte])
            
        # log the shift values to db
        self.client.write_points([{"measurement":self.args.get("log_measurement", "shift_heating_setpoint_no_name"),"fields":{"shift_kelvin_calculated":float(shift_kelvin), "shift_kelvin_limited":float(shift_kelvin_limited)}}])
        self.log("Shift Kelvin - calculated: {} / limited: {}".format(round(shift_kelvin,1), round(shift_kelvin_limited,1)))

    def get_list_of_derivatives(self):
        der_list = []
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time > now() - 24h ORDER BY time DESC'.format(self.db_field, self.db_measurement)
        result_points = self.client.query(query).get_points()
        for minute_value in self.minutes_for_evaltuation:
            #self.log(minute_value)
            newest_value = None
            current_time = None
            for point in result_points:
                #self.log(point)
                if newest_value == None:
                    newest_value = point[self.db_field]
                    current_time = datetime.datetime.utcnow()
                    #self.log(current_time.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    delta_value = point[self.db_field] - newest_value
                    delta_time = current_time - datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f')
                    #self.log(datetime.datetime.strptime(point["time"][:-4], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S"))
                    delta_time_seconds = delta_time.total_seconds()
                    #self.log("Delta seconds: {} minutes: {}".format(delta_time_seconds, round(delta_time_seconds/60,1)))
                    if delta_time_seconds >= (minute_value*60):
                        #self.log("Minute Value reached with delta seconds: {}".format(delta_time_seconds))
                        derivative = delta_value / (delta_time_seconds / 3600)
                        self.log("Minute: {} - Delta_K: {} (histoy: {} - now {}) - Derivative: {}".format(minute_value, delta_value, point[self.db_field], newest_value, derivative))
                        #self.log("Derivative: {}".format(derivative))
                        der_list.append(derivative)
                        break
        self.log(der_list)
        return der_list
    
    def shift_kelvin_to_byte_value(self, shift_kelvin):
        # get the value in K of one shifting point, as it is set in the config of the heating actuator. Defaults to 0.1 K
        shift_value = self.args.get("shift_value", 0.1)
        shift_points = round(shift_kelvin / shift_value)
        #self.log("Shift-Points: {}".format(shift_points))
        if shift_points > 0:
            value_byte = shift_points
        elif shift_points < 0:
            value_byte = 256 + shift_points
        else:
            value_byte = 0
        return value_byte
    
    def on_off_switch(self, entity, attribute, old, new, kwargs):
        if new == "off" and old != new:
            self.call_service("knx/send", address = self.args.get("ga_setpoint_shift"), payload = [0])
            self.log("Reset Setpoint Shift to 0")
            # log the shift values to db
            self.client.write_points([{"measurement":self.args.get("log_measurement", "shift_heating_setpoint_no_name"),"fields":{"shift_kelvin_calculated":float(0), "shift_kelvin_limited":float(0)}}])
    
    def drop(self):
        self.client.drop_measurement("test_heating_controller_ez")
