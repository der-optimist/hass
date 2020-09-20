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
        self.listen_state(self.waschmaschine_geleert, "binary_sensor.lumi_lumi_sensor_magnet_aq2_ddf99f04_on_off", new = "on")
        self.listen_state(self.trockner_fertig, "binary_sensor.trockner_ist_an", new = "off", old = "on")
        self.listen_state(self.trockner_geleert, "binary_sensor.trockner_ist_geleert", new = "on")
        self.switch_reminder_wm = "switch.reminder_waschmaschine_leeren"
        # define WM switch
        icon_reminder_wm = "/local/icons/reminders/washing-machine_orange_blink.svg"
        self.attributes_reminder_wm = {"entity_picture": icon_reminder_wm, "friendly_name": "Waschmaschine ist fertig"}
        self.timer_handle_wm = None
        self.timer_handle_wm_open = None
        # define dryer switch
        self.switch_reminder_tr = "switch.reminder_trockner_leeren"
        icon_reminder_tr = "/local/icons/reminders/dryer_orange_blink.svg"
        self.attributes_reminder_tr = {"entity_picture": icon_reminder_tr, "friendly_name": "Trockner ist fertig"}
        self.timer_handle_tr = None
    
    def waschmaschine_fertig(self, entity, attribute, old, new, kwargs):
        #self.fire_event("custom_notify", message="WM fertig, aber noch zu", target="telegram_jo")
        self.timer_handle_wm_open = self.run_in(self.waschmaschine_fertig_delayed, 180)
    
    def waschmaschine_fertig_delayed(self, kwargs):
        self.timer_handle_wm_open = None
        self.set_state(self.switch_reminder_wm, state = "on", attributes = self.attributes_reminder_wm)
        self.timer_handle_wm = self.run_in(self.remind_waschmaschine,3600)
        #self.fire_event("custom_notify", message="WM fertig", target="telegram_jo")
        
    def waschmaschine_geleert(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.switch_reminder_wm) == "on":
            #self.fire_event("custom_notify", message="WM geleert", target="telegram_jo")
        self.set_state(self.switch_reminder_wm, state = "off", attributes = self.attributes_reminder_wm)
        if self.timer_handle_wm_open != None:
            self.cancel_timer(self.timer_handle_wm_open)
            self.timer_handle_wm_open = None
        if self.timer_handle_wm != None:
            self.cancel_timer(self.timer_handle_wm)
            self.timer_handle_wm = None

    def trockner_fertig(self, entity, attribute, old, new, kwargs):
        if self.get_state("binary_sensor.trockner_ist_geleert") == "off":
            self.set_state(self.switch_reminder_tr, state = "on", attributes = self.attributes_reminder_tr)
            self.timer_handle_tr = self.run_in(self.remind_trockner,7200)
            #self.fire_event("custom_notify", message="TR fertig", target="telegram_jo")
        else:
            self.log("Trockner als fertig erkannt, ist aber wohl schon geleert. Werde keine Erinnerung ausloesen")

    def trockner_geleert(self, entity, attribute, old, new, kwargs):
        self.set_state(self.switch_reminder_tr, state = "off", attributes = self.attributes_reminder_tr)
        if self.timer_handle_tr != None:
            self.cancel_timer(self.timer_handle_tr)
            self.timer_handle_tr = None
        #self.fire_event("custom_notify", message="TR geleert", target="telegram_jo")

    def remind_waschmaschine(self, kwargs):
        message = "Waschmaschine ist seit einer Stunde fertig"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
        self.fire_event("custom_notify", message=message, target="telegram_ma")

    def remind_trockner(self, kwargs):
        message = "Trockner ist seit 2 Stunden fertig"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
        self.fire_event("custom_notify", message=message, target="telegram_ma")
