import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App does:
#  - Calculate "real" electricity meter value from KNX counter
#  - Create Sensor with this value
#  - Calculate power (from previous to current event)
#
# Args:
# knx_counter = "sensor.stromzahler_xyz_rohdaten"
# ha_electricity_sensor_name = "sensor.stromzahler_xyz"
# ha_electricity_sensor_friendly_name = "Stromzähler XYZ"
# ha_power_sensor_name = "sensor.el_leistung_xyz"
# ha_power_sensor_friendly_name = "El. Leistung XYZ"
# energy_per_pulse = 0.0005 (in kWh => 2000 pulses per kWh => 0.0005 kWh/pulse)
#

class stromzaehler_be(hass.Hass):

    def initialize(self):
        # listen for new values
        self.listen_state(self.counter_changed, self.args["knx_counter"])
        # initialize internal variables
        self.time_of_last_event = None
        self.value_of_last_event = None
        # set sensor values to zero until first values can be calculated
        self.log("Test: gibt es beim Neustart gleich einen Wert fuer den KNX counter?")
        self.log(self.get_state(self.args["knx_counter"]))
        # ich geh erst mal davon aus, dass der Wert nicht zur Verfügung steht und setze den Sensor auf 0
        self.set_state(self.args["ha_electricity_sensor_name"], state = 0, attributes={"icon":"mdi:counter", "friendly_name": self.args["ha_electricity_sensor_friendly_name"]})
        self.set_state(self.args["ha_power_sensor_name"], state = 0, attributes={"icon":"mdi:speedometer", "friendly_name": self.args["ha_power_sensor_friendly_name"]})
        
    def counter_changed(self, entity, attribute, old, new, kwargs):
        self.log("Value {} received from counter {}".format(new,self.args["knx_counter"])
        # Update electricity meter sensor
        new_electricity_value = new * self.args["energy_per_pulse"]
        self.set_state(self.args["ha_electricity_sensor_name"], state = new_electricity_value)
        # calculate power
        if self.time_of_last_event == None:
            self.log("Looks like it is the first event since a restart")
        else:
            if self.value_of_last_event == None:
                self.log("I have a time of the last event, but no value... no idea how that can happen. Look for a bug!")
            else:
                current_time = datetime.datetime.now()
                time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
                electricity_delta_Ws = (new - self.value_of_last_event) * self.args["energy_per_pulse"] * 3600 * 1000
                current_power = electricity_delta_Ws / time_delta_seconds
                self.set_state(self.args["ha_power_sensor_name"], state = current_power)
        # save current values in variables for next calculation
        self.time_of_last_event = current_time
        self.value_of_last_event = new
