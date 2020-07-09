import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Turn on or off a switch at certain time of day
#
# Args: 
# - switch_entity => switch.abc
# - time => string => "18:00"
# - on_off => string => "on" of "off" (with ")
# 

class turn_switches_on_off(hass.Hass):

    def initialize(self):
        hour = self.args["time"].split(":")[0]
        minute = self.args["time"].split(":")[1]
        self.run_daily(self.turn_on_off_switch, datetime.time(int(hour), int(minute), 0))

    def turn_on_off_switch(self, kwargs):
        if self.args["on_off"] == "on":
            self.log("Will turn on switch {}".format(self.args["switch_entity"]))
            self.turn_on(self.args["switch_entity"])
        elif self.args["on_off"] == "off":
            self.log("Will turn off switch {}".format(self.args["switch_entity"]))
            self.turn_off(self.args["switch_entity"])
        else:
            self.log("Arg on_off should be on or off as a string")
