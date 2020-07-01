import appdaemon.plugins.hass.hassapi as hass

#
# App to handle HA errors
#
# Args: 
# 

class error_handling(hass.Hass):

    def initialize(self):
        self.listen_event(self.error_event, "system_log_event", level = "ERROR")

    def error_event(self,event_name,data,kwargs):
        message = "Home Assistant Error"\
                  "source: "\
                  "{}"\
                  "message: "\
                  "{}"\
                  "exception:"\
                  "{}".format(data["source"],data["message"],data["exception"])
        self.fire_event("custom_notify", message=message, target="telegram_jo")
        if data["source"] == "homeassistant.core" and data["message"].startswith("Error doing job: Task exception was never retrieved"):
            self.fire_event("custom_notify", message="KNX-Fehler erkannt", target="telegram_jo")
