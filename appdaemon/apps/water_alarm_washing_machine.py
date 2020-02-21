import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when status matches given status:
#
# Args:
# none
#

class water_alarm_washing_machine(hass.Hass):

    def initialize(self):
        self.run_in(self.initialize_delayed, 16)
        
    def initialize_delayed(self, kwargs):
        self.listen_state(self.eimer_hebeanlage_voll, "binary_sensor.eimer_hebeanlage_voll", new = "on")
        self.listen_state(self.wasser_boden, "binary_sensor.wasser_boden_bei_hebeanlage", new = "on")
        self.listen_state(self.sicherung_hebeanlage_raus, "binary_sensor.sicherung_keller_sd_rausgeflogen", new = "on")
    
    def eimer_hebeanlage_voll(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Eimer Hebeanlage voll - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message", target="telegram_jo")
            self.fire_event("custom_notify", message=message", target="telegram_ma")
                            
    def wasser_boden(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Wasser auf dem Boden bei der Hebeanlage - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message", target="telegram_jo")
            self.fire_event("custom_notify", message=message", target="telegram_ma")

    def sicherung_hebeanlage_raus(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Sicherung Keller-Steckdosen (Hebeanlage!) rausgeflogen - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message", target="telegram_jo")
            self.fire_event("custom_notify", message=message", target="telegram_ma")
