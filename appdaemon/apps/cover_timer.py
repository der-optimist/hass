import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Set cover position at a specific time
#
# Args: 
# - cover_entity => cover.jal_abc
# - time => string => "18:00"
# - position => 100
# - tilt => 100
# 

class cover_timer(hass.Hass):

    def initialize(self):
        hour = self.args["time"].split(":")[0]
        minute = self.args["time"].split(":")[1]
        self.run_daily(self.set_cover_position, datetime.time(int(hour), int(minute), 0))

    def set_cover_position(self, kwargs):
        self.log("Will set {} to position {} and tilt-position {}".format(self.args["cover_entity"],self.args["position"],self.args["tilt"]))
        self.call_service("cover/set_cover_position", entity_id = self.args["cover_entity"], position = self.args["position"])
        self.call_service("cover/set_cover_tilt_position", entity_id = self.args["cover_entity"], tilt_position = self.args["tilt"])
    
