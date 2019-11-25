import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App does:
#  - Calculate "real" electricity meter value from KNX pulse counter (to kWh)
#  - Create Sensor with this value
#  - Calculate power in W (from previous to current event)
#
# Args:
# knx_counter = "sensor.stromzahler_xyz_rohdaten"
# ha_electricity_sensor_name = "sensor.stromzahler_xyz"
# ha_electricity_sensor_friendly_name = "Stromzähler XYZ"
# ha_power_sensor_name = "sensor.el_leistung_xyz"
# ha_power_sensor_friendly_name = "El. Leistung XYZ"
# energy_per_pulse = 0.0005 (in kWh => 2000 pulses per kWh => 0.0005 kWh/pulse)
# knx_sending_every = 5 (expect to receive a new value after 10 pulses. Used only for calulating ramp-down values)
# cut_power_below: 10 (set to 0 if ramp-down goes below this value)
#

class counter_to_power_meter(hass.Hass):

    def initialize(self):
        # listen for new values
        self.listen_state(self.counter_changed, self.args["knx_counter"])
        # initialize internal variables
        self.time_of_last_event = None
        self.value_of_last_event = None
        self.handle_ramp_down_timer = None
        try:
            current_electricity = round(self.get_state(self.args["ha_electricity_sensor_name"]))
        except:
            current_electricity = 0
        self.set_state(self.args["ha_electricity_sensor_name"], state = current_electricity, attributes={"icon":"mdi:counter", "friendly_name": self.args["ha_electricity_sensor_friendly_name"], "unit_of_measurement": "kWh"})
        self.set_state(self.args["ha_power_sensor_name"], state = 0, attributes={"icon":"mdi:speedometer", "friendly_name": self.args["ha_power_sensor_friendly_name"], "unit_of_measurement": "W"})
        
    def counter_changed(self, entity, attribute, old, new, kwargs):
        if new == "unavailable" or new == "Nicht verfügbar" or new == old:
            return
        if self.handle_ramp_down_timer != None:
            self.cancel_timer(self.handle_ramp_down_timer)
        current_time = datetime.datetime.now() # for most accurate value, capture current time first
        # Update electricity meter sensor
        new_electricity_value = float(new) * self.args["energy_per_pulse"]
        self.set_state(self.args["ha_electricity_sensor_name"], state = round(new_electricity_value))
        # calculate power
        if self.time_of_last_event == None:
            self.log("Looks like it is the first event since a restart. Power will be available next time")
        else:
            if self.value_of_last_event == None:
                self.log("I have a time of the last event, but no value... no idea how that can happen. Look for a bug!")
            else:
                time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
                electricity_delta_Ws = (float(new) - self.value_of_last_event) * self.args["energy_per_pulse"] * 3600 * 1000
                current_power = electricity_delta_Ws / time_delta_seconds
                self.set_state(self.args["ha_power_sensor_name"], state = round(current_power, 1))
                self.log("Value {} received from counter {}. Calculated new power value: {}".format(new,self.args["knx_counter"],round(current_power, 1)))
                self.handle_ramp_down_timer = self.run_in(self.ramp_down,round(2 * time_delta_seconds + 1))
        # save current values in variables for next calculation
        self.time_of_last_event = current_time
        self.value_of_last_event = float(new)

    def ramp_down(self, kwargs):
        current_time = datetime.datetime.now() # for most accurate value, capture current time first
#        new_virtual_electricity_value = (self.value_of_last_event + self.args["knx_sending_every"]) * self.args["energy_per_pulse"]
        time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
        electricity_delta_Ws = self.args["knx_sending_every"] * self.args["energy_per_pulse"] * 3600 * 1000
        current_power = electricity_delta_Ws / time_delta_seconds
        if current_power < self.args["cut_power_below"]:
            self.set_state(self.args["ha_power_sensor_name"], state = 0)
            self.log("Rampdown limit of counter {} reached. Will set new power to 0".format(self.args["knx_counter"]))
        else:
            self.set_state(self.args["ha_power_sensor_name"], state = round(current_power, 1))
            self.log("Rampdown set counter {} to new power value: {}".format(self.args["knx_counter"],round(current_power, 1)))
            self.handle_ramp_down_timer = self.run_in(self.ramp_down,round(time_delta_seconds + 0.5))
