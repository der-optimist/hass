import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle garbage topics
#
# Args: 
# 

class log_events(hass.Hass):

    def initialize(self):
        self.listen_event(self.log_all_events)
    
    def log_all_events(self, event_name, data, kwargs):
        self.log(event_name)
        self.log(data)
