import appdaemon.plugins.hass.hassapi as hass
import random

# 
# App to trigger a "knx expose" for a sensor ever X minutes
#
# Args:
#  - sensor_name
#  - interval_minutes

class expose_sensor_to_knx(hass.Hass):

    def initialize(self):
        self.run_every(self.trigger_expose,60*self.args["interval_minutes"])

    def trigger_expose(self, kwargs):
        random_number = random.randint(0,1e9)
        current_state = self.get_state(self.args["sensor_name"])
        attributes = self.get_state(self.args["sensor_name"], attribute="all")
        attributes["random_number"] = random_number
        self.set_state(self.args["sensor_name"], state = current_state, attributes = attributes)
