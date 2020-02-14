import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when status matches given status:
#
# Args:
# - entity
# - status_to_match
# - notify_target
# - message
#

class notify_when_status_matched(hass.Hass):

    def initialize(self):
        self.listen_state(self.sensor_state_changed, self.args["entity"], new = self.args["status_to_match"])
    
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.fire_event("custom_notify", message=self.args["message"], target=self.args["notify_target"])
