import appdaemon.plugins.hass.hassapi as hass

#
# App to test input constraint
#
# Args: 
# 

class test(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change, "switch.dummy_light_switch")
    
    def state_change(self, entity, attributes, old, new, kwargs):
        self.log("Schalter betätigt: {}".format(new))
