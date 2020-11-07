import appdaemon.plugins.hass.hassapi as hass
from fritzconnection.lib.fritzcall import FritzCall
import requests

#
# App to turn the washing machine off in critical cases
#
# Args:
# none
#

class water_alarm_washing_machine(hass.Hass):

    def initialize(self):
    	self.url = "http://192.168.178.42:2971/api/command"
        self.run_in(self.initialize_delayed, 16)
        
    def initialize_delayed(self, kwargs):
        self.listen_state(self.eimer_hebeanlage_voll, "binary_sensor.eimer_hebeanlage_voll", new = "on")
        self.listen_state(self.wasser_boden, "binary_sensor.wasser_boden_bei_hebeanlage", new = "on")
        self.listen_state(self.sicherung_hebeanlage_raus, "binary_sensor.sicherung_keller_sd_rausgeflogen", new = "on")
        self.listen_event(self.button_wm_strom_an, "zha_event", device_ieee = "00:15:8d:00:04:0b:11:2f", command = "right_single")
    
    def eimer_hebeanlage_voll(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Eimer Hebeanlage voll - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            try:
                requests.post(self.url, json={"speak":"Alarm! Eimer Hebeanlage ist voll"}, timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])
                            
    def wasser_boden(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Wasser auf dem Boden bei der Hebeanlage - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            try:
                requests.post(self.url, json={"speak":"Alarm! Wasser auf dem Boden bei der Hebeanlage"}, timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])

    def sicherung_hebeanlage_raus(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Sicherung Keller-Steckdosen (Hebeanlage!) rausgeflogen - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            try:
                requests.post(self.url, json={"speak":"Achtung! Hebeanlage hat keinen Strom"}, timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])
            
    def button_wm_strom_an(self,event_name,data,kwargs):
        self.turn_on("switch.waschmaschine")
        message = "Waschmaschine hat (wieder) Strom"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
