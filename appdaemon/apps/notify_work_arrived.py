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
        self.listen_state(self.arrived, self.args["device"], new = self.args["zone"])
        
    def arrived(self, entity, attribute, old, new, kwargs):
        self.log("Jo arrived at work")
        self.notify("Angekommen", name = "telegram_jo")
