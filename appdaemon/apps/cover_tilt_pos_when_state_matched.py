import appdaemon.plugins.hass.hassapi as hass

#
# set cover to "Sichtschutz" when...
#
# Args: 
# - cover_entity => cover.jal_abc
# - mode (tilt or tilt_pos)
# - target_tilt
# - target_position (only if mode = tilt_pos)
# - match_entity
# - match_state_new
# - match_state_old
# 

class cover_tilt_pos_when_state_matched(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_matched, self.args["match_entity"], old = self.args["match_state_old"], new = self.args["match_state_new"])

    def state_matched(self, entity, attributes, old, new, kwargs):
        if self.args["mode"] == "tilt":
            if float(self.get_state(self.args["cover_entity"], attribute="current_position")) > 0:
                self.call_service("cover/set_cover_tilt_position", entity_id = self.args["cover_entity"], tilt_position = self.args["target_tilt"])
                self.log("Habe Jalousie {} auf Winkel {} gestellt".format(self.args["cover_entity"],self.args["target_tilt"]))
            else:
                self.log("Sollte Jalousie {} auf Winkel {} stellen, sie war aber oben. Habe nichts gemacht".format(self.args["cover_entity"],self.args["target_tilt"]))
        elif self.args["mode"] == "tilt_pos":
            self.call_service("cover/set_cover_position", entity_id = self.args["cover_entity"], position = self.args["target_position"])
            self.call_service("cover/set_cover_tilt_position", entity_id = self.args["cover_entity"], tilt_position = self.args["target_tilt"])
        else:
            self.log("mode should be tilt or tilt_pos")
