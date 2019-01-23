import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when arrived at work
#
# Args:
# zone = Name of zone
# device = tracked device
#

class notify_work_arrived(hass.Hass):

    def initialize(self):
        device_full = "device_tracker." + self.args["device"]
        self.listen_state(self.arrived, device_full, new = self.args["zone"])
        
    def arrived(self, entity, attribute, old, new, kwargs):
        self.log("Arrived at work")
