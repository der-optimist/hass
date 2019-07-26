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
#

class counter_to_power_meter(hass.Hass):

    def initialize(self):
        # listen for new values
        self.listen_state(self.counter_changed, self.args["knx_counter"])
        # initialize internal variables
        self.time_of_last_event = None
        self.value_of_last_event = None
        self.handle_reset_timer = None
        # set sensor values to zero until first values can be calculated
        self.log("Test: gibt es beim Neustart gleich einen Wert fuer den KNX counter?")
        self.log(self.get_state(self.args["knx_counter"]))
        # ich geh erst mal davon aus, dass der Wert nicht zur Verfügung steht und setze den Sensor auf 0
        self.set_state(self.args["ha_electricity_sensor_name"], state = 0, attributes={"icon":"mdi:counter", "friendly_name": self.args["ha_electricity_sensor_friendly_name"], "unit_of_measurement": "kWh"})
        self.set_state(self.args["ha_power_sensor_name"], state = 0, attributes={"icon":"mdi:speedometer", "friendly_name": self.args["ha_power_sensor_friendly_name"], "unit_of_measurement": "W"})
        
    def counter_changed(self, entity, attribute, old, new, kwargs):
        if new == "unavailable" or new == "Nicht verfügbar" or new == old:
            return
        if self.handle_reset_timer != None:
            self.cancel_timer(self.handle_reset_timer)
        current_time = datetime.datetime.now() # for most accurate value, capture current time first
        self.log("Value {} received from counter {}".format(new,self.args["knx_counter"]))
        # Update electricity meter sensor
        new_electricity_value = new * self.args["energy_per_pulse"]
        self.set_state(self.args["ha_electricity_sensor_name"], state = new_electricity_value)
        # calculate power
        if self.time_of_last_event == None:
            self.log("Looks like it is the first event since a restart. Power will be available next time")
        else:
            if self.value_of_last_event == None:
                self.log("I have a time of the last event, but no value... no idea how that can happen. Look for a bug!")
            else:
                time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
                electricity_delta_Ws = (new - self.value_of_last_event) * self.args["energy_per_pulse"] * 3600 * 1000
                current_power = electricity_delta_Ws / time_delta_seconds
                self.set_state(self.args["ha_power_sensor_name"], state = current_power)
        # save current values in variables for next calculation
        self.time_of_last_event = current_time
        self.value_of_last_event = new
        self.handle_reset_timer = self.run_in(self.reset_power,10*60) # no value for 10 min => 0. Means power below 3W (2000 pulses/kWh)

    def reset_power(self, kwargs):
        self.set_state(self.args["ha_power_sensor_name"], state = 0)

# to do: Timer alle 60 Sekunden, Power so berechnen als wäre gerade ein neuer Wert gekommen => Power sink langsam. Abbrechen wenn unter ...W
