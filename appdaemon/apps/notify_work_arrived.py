import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when arrived at work
#
# Args:
# zone = Name of zone
# device = tracked device
#

class notify_by_location(hass.Hass):

    def initialize(self):
        self.listen_state(self.arrived, self.args["device"], new = self.args["zone"])
        
    def arrived(self, entity, attribute, old, new, kwargs):
        self.log("Arrived at work")
