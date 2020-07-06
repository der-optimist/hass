import appdaemon.plugins.hass.hassapi as hass

#
# App to handle HA errors
#
# Args: 
# 

class error_handling(hass.Hass):

    def initialize(self):
        self.listen_event(self.error_event, "system_log_event", level = "ERROR")
#        self.listen_event(self.warning_event, "system_log_event", level = "WARNING")

    def error_event(self,event_name,data,kwargs):
        self.log("Error erkannt. Source ist {}".format(data["source"]))
        if not ("telegram api limit" in data["message"] or "Flood control exceeded" in data["message"] or "Message is too long" in data["message"]):
            message = "Home Assistant ERROR\n"\
                      "source:\n"\
                      "{}\n"\
                      "message:\n"\
                      "{}\n"\
                      "exception:\n"\
                      "{}".format(data["source"],data["message"],data["exception"])
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            if "knx" in data["source"] and "Error doing job: Task exception was never retrieved" in data["message"]:
                self.fire_event("custom_notify", message="KNX-Fehler erkannt. Werde HA in 30 Sekunden neu starten", target="telegram_jo")
                self.log("KNX Error erkannt. Werde in 30s HA neu starten")
                self.run_in(self.restart_ha,30)
    
    def restart_ha(self, kwargs):
        self.call_service("homeassistant/restart")

    def warning_event(self,event_name,data,kwargs):
        self.log("Warning erkannt. Source ist {}".format(data["source"]))
        message = "Home Assistant WARNING\n"\
                  "source:\n"\
                  "{}\n"\
                  "message:\n"\
                  "{}\n"\
                  "exception:\n"\
                  "{}".format(data["source"],data["message"],data["exception"])
        self.fire_event("custom_notify", message=message, target="telegram_jo")
