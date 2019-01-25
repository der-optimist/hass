import appdaemon.plugins.hass.hassapi as hass

#
# App to handle garbage topics
#
# Args: 
#

class garbage(hass.Hass):

    def initialize(self):
        self.listen_state(self.check_next_day)
        
    def check_next_day(self, entity, attribute, old, new, kwargs):
        pass
