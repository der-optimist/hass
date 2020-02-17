import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when status matches given status:
#
# Args:
# - entity
# - status_to_match
# - previous_status (optional, can avoid notifications on startup)
# - notify_target
# - special_bot_api_key (only if notify_target = special_bot. Token of a telegram bot)
# - special_bot_chat_id (only if notify_target = special_bot. Chat-ID the message should be sent to. Group-ID or personal telegram ID)
# - message
# - init_delay (min. 1)
#

class notify_when_status_matched(hass.Hass):

    def initialize(self):
        self.run_in(self.initialize_delayed, int(self.args["init_delay"]))
        
    def initialize_delayed(self, kwargs):
        if self.args.get("previous_status", None) == None:
            #self.log("prev_state ist None")
            self.listen_state(self.sensor_state_changed, self.args["entity"], new = self.args["status_to_match"])
        else:
            self.listen_state(self.sensor_state_changed, self.args["entity"], new = self.args["status_to_match"], old = self.args["previous_status"])
            #self.log("prev_state ist {}".format(self.args["previous_status"]))
    
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        if new != old:
            if self.args["notify_target"] == "special_bot":
                if self.args.get("special_bot_api_key", None) == None or self.args.get("special_bot_chat_id", None) == None:
                    self.log("When target is special bot, the special_bot_api_key and special_bot_chat_id must be provided!")
                else:
                    self.fire_event("custom_notify", message=self.args["message"], target=self.args["notify_target"], special_bot_api_key=self.args["special_bot_api_key"], special_bot_chat_id=self.args["special_bot_chat_id"])
                    self.log("fired message to special bot")
            else:
                self.fire_event("custom_notify", message=self.args["message"], target=self.args["notify_target"])
                self.log("fired message to standard target")
