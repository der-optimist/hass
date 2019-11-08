import appdaemon.plugins.hass.hassapi as hass

#
# Some of my apps use switches as reminders (e.g. garbage and calendar_and_reminders)
# This app handles the events when I click the switch on the UI
#
# Args: no args required
# 

class toggle_self_created_switches(hass.Hass):

    def initialize(self):
        # --- listen for events of self created switches (they are not handeled by HA)
        self.listen_event(self.toggle_switches, event = "call_service")
        
    def toggle_switches(self,event_name,data, kwargs):
        try:
            entity_id = data["service_data"]["entity_id"]
            if "switch.reminder" in entity_id or "switch.schlafen_oder_aufwachen" in entity_id:
                if data["service"] == "turn_off":
                    self.log(entity_id + " switched off")
                    self.set_state(entity_id, state = "off")
                if data["service"] == "turn_on":
                    self.log(entity_id + " switched on")
                    self.set_state(entity_id, state = "on")
        except KeyError:
            pass
