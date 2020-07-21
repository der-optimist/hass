import appdaemon.plugins.hass.hassapi as hass

#
# make custom reminders survive a restart
#
# Args: 
# 

class save_reminders(hass.Hass):

    def initialize(self):
        self.set_textvalue("input_text.saved_reminder_001", "reminder_name", icon="/local/icons/reminders/exclamation_mark_blink.svg")
        #self.listen_state(self.illuminance_changed, self.args["illuminance_sensor"])

    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        pass
