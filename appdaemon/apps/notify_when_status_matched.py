import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when status matches given status:
#
# Args:
# - entity
# - status_to_match
# - previous_status (optional, can avoid notifications on startup)
# - notify_target
# - message
# - init_delay (min. 1)
#

class notify_when_status_matched(hass.Hass):

    def initialize(self):
        self.run_in(self.initialize_delayed, int(self.args["previous_status"]))
        
    def initialize_delayed(self, kwargs):
        if self.args["previous_status"] == None:
            self.log("prev_state ist None")
            self.listen_state(self.sensor_state_changed, self.args["entity"], new = self.args["status_to_match"])
        else:
            self.listen_state(self.sensor_state_changed, self.args["entity"], new = self.args["status_to_match"], old = self.args["previous_status"])
            self.log("prev_state ist {}".format(self.args["previous_status"]))
    
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.fire_event("custom_notify", message=self.args["message"], target=self.args["notify_target"])
