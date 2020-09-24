import appdaemon.plugins.hass.hassapi as hass
import datetime

# 
# App to trigger a "knx expose" for a sensor ever X minutes
#
# Args:
#  - sensor_entity
#  - interval_minutes

class expose_sensor_to_knx(hass.Hass):

    def initialize(self):
        # wait for KNX entities 
        delay_seconds = self.args["init_delay_minutes"]*60
        self.up_down = "down"
        self.run_in(self.initialize_delayed,delay_seconds)

    def initialize_delayed(self, kwargs):
        interval = int(60 * self.args["interval_minutes"])
        self.run_every(self.trigger_expose, (datetime.datetime.now() + datetime.timedelta(seconds=5)), interval)

    def trigger_expose(self, kwargs):
        random_number = random.randint(0,1e9)
        current_state = self.get_state(self.args["sensor_entity"])
        try:
            if self.up_down == "down":
                current_state = float(current_state) - 0.0001
                self.up_down = "up"
            else:
                current_state = float(current_state) + 0.0001
                self.up_down = "down"
        except Exception as e:
            self.log("Error modifing sensor state. Error was {}".format(e))
        attributes = self.get_state(self.args["sensor_entity"], attribute="all")["attributes"]
        self.set_state(self.args["sensor_entity"], state = current_state, attributes = attributes)
