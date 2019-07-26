import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App does:
#  - Some KNX sensors don't get a "unit_of_measurement" or an icon at startup. This app shall update them
#
# Args:
# none

class set_sensor_attributes(hass.Hass):

    def initialize(self):
        # listen for new values
        self.run_in(self.set_attributes, 1)
  
    def set_attributes(self, kwargs):
        for sensor in self.get_state("sensor"):
            self.log(sensor)
