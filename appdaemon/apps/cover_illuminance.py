import appdaemon.plugins.hass.hassapi as hass

#
# set cover when passing an illuminance value
#
# Args: 
# - cover_entity => cover.jal_abc
# - illuminance_sensor => sensor.ill_abc
# - illuminance => 2 (lx)
# - up_or_down => either up or down
# - position => 100
# - tilt => 100
# 

class cover_illuminance(hass.Hass):

    def initialize(self):
        self.listen_state(self.illuminance_changed, self.args["illuminance_sensor"])

    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        if self.args["up_or_down"] == "down" and  new <= float(self.args["illuminance"]) and old > float(self.args["illuminance"]):
            self.log("Getting dark now, will set cover {} to position {} and tilt {} now.".format(self.args["cover_entity"],self.args["position"],self.args["tilt"]))
            self.call_service("cover/set_cover_position", entity_id = self.args["cover_entity"], position = self.args["position"])
            self.call_service("cover/set_cover_tilt_position", entity_id = self.args["cover_entity"], tilt_position = self.args["tilt"])
        if self.args["up_or_down"] == "up" and  new >= float(self.args["illuminance"]) and old < float(self.args["illuminance"]):
            self.log("Getting bright now, will set cover {} to position {} and tilt {} now.".format(self.args["cover_entity"],self.args["position"],self.args["tilt"]))
            self.call_service("cover/set_cover_position", entity_id = self.args["cover_entity"], position = self.args["position"])
            self.call_service("cover/set_cover_tilt_position", entity_id = self.args["cover_entity"], tilt_position = self.args["tilt"])
