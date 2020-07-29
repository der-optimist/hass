import appdaemon.plugins.hass.hassapi as hass
import random
import datetime

# 
# App to trigger a "knx expose" for a sensor ever X minutes
#
# Args:
#  - sensor_entity
#  - interval_minutes

class expose_sensor_to_knx(hass.Hass):

    def initialize(self):
        start_time = datetime.time(0, 3, random.randint(0,59)) 
        interval = int(60 * self.args["interval_minutes"])
        self.run_every(self.trigger_expose, start_time, interval)

    def trigger_expose(self, kwargs):
        random_number = random.randint(0,1e9)
        current_state = self.get_state(self.args["sensor_entity"])
        attributes = self.get_state(self.args["sensor_entity"], attribute="all")
        attributes["random_number"] = random_number
        self.set_state(self.args["sensor_entity"], state = current_state, attributes = attributes)
