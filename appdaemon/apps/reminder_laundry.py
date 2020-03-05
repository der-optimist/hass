import appdaemon.plugins.hass.hassapi as hass

#
# App to remind if washing mashine or dryer are done
#
# Args:
# none
#

class reminder_laundry(hass.Hass):

    def initialize(self):
        self.listen_state(self.waschmaschine_fertig, "binary_sensor.waschmaschine_ist_an", new = "off", old = "on")
        self.listen_state(self.waschmaschine_geleert, "binary_sensor.pm_k_te", new = "on")
        self.listen_state(self.trockner_fertig, "binary_sensor.trockner_ist_an", new = "off", old = "on")
        self.listen_state(self.trockner_geleert, "binary_sensor.trockner_ist_geleert", new = "on")
        self.switch_reminder_wm = "switch.reminder_waschmaschine_leeren"
        self.attributes_reminder_wm = {"icon": "mdi:washing-machine", "friendly_name": "Waschmaschine ist fertig"}
        self.timer_handle_wm = None
        self.switch_reminder_tr = "switch.reminder_trockner_leeren"
        self.attributes_reminder_tr = {"icon": "mdi:tumble-dryer", "friendly_name": "Trockner ist fertig"}
        self.timer_handle_tr = None
    
    def waschmaschine_fertig(self, entity, attribute, old, new, kwargs):
        self.set_state(self.switch_reminder_wm, state = "on", attributes = self.attributes_reminder_wm)
        self.timer_handle_wm = self.run_in(self.remind_waschmaschine,600)
        
    def waschmaschine_geleert(self, entity, attribute, old, new, kwargs):
        self.set_state(self.switch_reminder_wm, state = "off", attributes = self.attributes_reminder_wm)
        if self.timer_handle_wm != None:
            self.cancel_timer(self.timer_handle_wm)
            self.timer_handle_wm = None

    def trockner_fertig(self, entity, attribute, old, new, kwargs):
        self.set_state(self.switch_reminder_tr, state = "on", attributes = self.attributes_reminder_tr)
        self.timer_handle_tr = self.run_in(self.remind_trockner,600)

    def trockner_geleert(self, entity, attribute, old, new, kwargs):
        self.set_state(self.switch_reminder_tr, state = "off", attributes = self.attributes_reminder_tr)
        if self.timer_handle_tr != None:
            self.cancel_timer(self.timer_handle_tr)
            self.timer_handle_tr = None

    def remind_waschmaschine(self, kwargs):
        message = "Waschmaschine ist seit 10 Minuten fertig"
        self.fire_event("custom_notify", message=message, target="telegram_jo")

    def remind_trockner(self, kwargs):
        message = "Trockner ist seit 10 Minuten fertig"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
