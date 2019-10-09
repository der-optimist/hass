import appdaemon.plugins.hass.hassapi as hass
from typing import Set
import datetime

#
# Automate light, universal app
#
# Args: 
# - light (light entity that should be controlled)
# - triggers (list of triggers)
# - brightness_values (list of time and brightness value pairs, for "basic" brightness depending on time)
# - min_illuminance_values (list of time and illuminance value pairs, for taget illuminance depending on time)
# - illuminance_sensor
# 

class auto_light_2(hass.Hass):

    def initialize(self):
        self.light: str = self.args.get("light")
        self.triggers: Set[str] = self.args.get("triggers", set())
        self.illuminance_sensor: str = self.args.get("illuminance_sensor", None)
        self.times_brightness_strings = self.args["brightness_values"].keys()
        self.find_last_brightness_value(None)

    def find_last_brightness_value(self, kwargs):
        now = datetime.datetime.now()
        for each in sorted(self.times_brightness_strings):
            if now >= now.replace(hour=int(each.split(":")[0]), minute=int(each.split(":")[1]), second=0, microsecond=0):
                self.basic_brightness = self.args["brightness_values"][each]
        self.log(self.basic_brightness)
        self.log(type(self.basic_brightness))

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
    
