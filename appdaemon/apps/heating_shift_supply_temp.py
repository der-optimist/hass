import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# What it does:
# Shift heating supply temp by adjusting room target temp
#
# What args it needs: see below
# 

class heating_shift_supply_temp(hass.Hass):

    def initialize(self):
        # args
        interval_hours = self.args["interval_hours"]
        self.temp_limit_max = self.args["temp_limit_max"]
        self.temp_limit_min = self.args["temp_limit_min"]
        self.valve_target_min = self.args["valve_target_min"]
        self.valve_target_max = self.args["valve_target_max"]
        self.step_size_up = self.args["step_size_up"]
        self.step_size_down = self.args["step_size_down"]
        self.heating_entity = self.args["heating_entity"]
        # run regularly
        time_first_run = datetime.datetime.strptime("00:03:03","%H:%M:%S")
        self.run_every(self.adjust_room_target_temp, time_first_run, interval_hours * 3600)
        # testing:
        #self.adjust_room_target_temp(None) # run at app startup

    def adjust_room_target_temp(self, kwargs):
        try:
            current_room_target_temp = float(self.get_state(self.heating_entity, attribute="temperature"))
            max_valve_value = float(self.get_state("sensor.stellwert_heizung_zeitverlauf_mean"))
        except Exception as e:
            self.log("Error reading current values. Error: {}".format(e))
            return
        if max_valve_value > self.valve_target_max:
            self.log("Should shift room target temp up")
            if current_room_target_temp < self.temp_limit_max:
                new_room_target_temp = current_room_target_temp + self.step_size_up
                self.log("Will shift room target temp from {} to {}".format(current_room_target_temp, new_room_target_temp))
                self.call_service("climate/set_temperature", entity_id = self.heating_entity, temperature = new_room_target_temp)
            else:
                self.log("... but limit is reached. current: {} - limit: {}".format(current_room_target_temp, self.temp_limit_max))
        elif max_valve_value < self.valve_target_min:
            self.log("Should shift room target temp down")
            if current_room_target_temp > self.temp_limit_min:
                new_room_target_temp = current_room_target_temp - self.step_size_down
                self.log("Will shift room target temp from {} to {}".format(current_room_target_temp, new_room_target_temp))
                self.call_service("climate/set_temperature", entity_id = self.heating_entity, temperature = new_room_target_temp)
            else:
                self.log("... but limit is reached. current: {} - limit: {}".format(current_room_target_temp, self.temp_limit_min))
        else:
            self.log("Valve max value in target range. Will do nothing. current valve max: {} - target range: {} - {}".format(max_valve_value, self.valve_target_min, self.valve_target_max))
