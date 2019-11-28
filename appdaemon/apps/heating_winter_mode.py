import appdaemon.plugins.hass.hassapi as hass

#
# Set KNX Winter Switch According to HA Input Boolean 
#
# Args:
# - input_booloean_entity
# - switch_entity
# 

class heating_winter_mode(hass.Hass):

    def initialize(self):
        # wait for KNX entities 
        self.run_in(self.initialize_delayed,110)
        self.listen_state(self.input_changed, self.args["input_booloean_entity"])
    
    def initialize_delayed(self, kwargs):
        if self.get_state(self.args["input_booloean_entity"]) == "on":
            self.turn_on(self.args["switch_entity"])
        if self.get_state(self.args["input_booloean_entity"]) == "off":
            self.turn_off(self.args["switch_entity"])
    
    def input_changed(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_on(self.args["switch_entity"])
        if new == "off":
            self.turn_off(self.args["switch_entity"])
