import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle the awesome pizza timer
#
# Args: 
# 

class pizza_timer(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change, "input_select.pizza_timer")
    
    def state_change(self, entity, attributes, old, new, kwargs):
        if new != None:
            self.log("State Change in Pizza Timer erkannt: {}".format(new))
