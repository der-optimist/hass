import appdaemon.plugins.hass.hassapi as hass
from typing import Set
import datetime

#
# Automate light, universal app
#
# Args: 
# - light (light entity that should be controlled)
# - triggers (list of triggers)
# - brightness_values (list of time and brightness value pairs, for "basic" brightness depending on time. "00:00": XY should be the first)
# - min_illuminance_values (list of time and illuminance value pairs, for taget illuminance depending on time. "00:00": XY should be the first)
# - illuminance_sensor
# 

class auto_light_2(hass.Hass):

    def initialize(self):
        self.light: str = self.args.get("light")
        self.triggers: Set[str] = self.args.get("triggers", set())
        self.illuminance_sensor: str = self.args.get("illuminance_sensor", None)
        # brightness depending on time
        self.times_brightness_strings = self.args["brightness_values"].keys()
        self.update_basic_brightness_value(None)
        for each in sorted(self.times_brightness_strings):
            self.run_daily(self.update_basic_brightness_value, datetime.time(int(each.split(":")[0]), int(each.split(":")[1]), 0))
        # min illuminance depending on time
        self.times_min_illuminance_strings = self.args["min_illuminance_values"].keys()
        self.update_min_illuminance_value(None)
        for each in sorted(self.times_min_illuminance_strings):
            self.run_daily(self.update_min_illuminance_value, datetime.time(int(each.split(":")[0]), int(each.split(":")[1]), 0))

    def update_basic_brightness_value(self, kwargs):
        now = datetime.datetime.now()
        for each in sorted(self.times_brightness_strings):
            if now >= now.replace(hour=int(each.split(":")[0]), minute=int(each.split(":")[1])):
                current_brightness = self.args["brightness_values"][each]
        self.basic_brightness = current_brightness
        self.log("Basic brightness set to {}".format(self.basic_brightness))

    def update_min_illuminance_value(self, kwargs):
        now = datetime.datetime.now()
        for each in sorted(self.times_min_illuminance_strings):
            if now >= now.replace(hour=int(each.split(":")[0]), minute=int(each.split(":")[1])):
                current_min_illuminance = self.args["min_illuminance_values"][each]
        self.min_illuminance = current_min_illuminance
        self.log("Min illuminance set to {}".format(self.min_illuminance))

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
    
