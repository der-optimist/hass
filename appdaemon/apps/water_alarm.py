import appdaemon.plugins.hass.hassapi as hass
from fritzconnection.lib.fritzcall import FritzCall
import requests

#
# App to turn the washing machine off in critical cases
#
# Args:
# none
#

class water_alarm(hass.Hass):

    def initialize(self):
        self.url = "http://192.168.178.42:2971/api/command"
        self.run_in(self.initialize_delayed, 16)
        
    def initialize_delayed(self, kwargs):
        self.listen_state(self.eimer_hebeanlage_voll, "binary_sensor.eimer_hebeanlage_voll", new = "on")
        self.listen_state(self.wasser_boden_hebeanlage, "binary_sensor.wasser_boden_bei_hebeanlage", new = "on")
        self.listen_state(self.sicherung_hebeanlage_raus, "binary_sensor.sicherung_keller_sd_rausgeflogen", new = "on")
        self.listen_state(self.wasser_boden_spuelmaschine, "binary_sensor.wasser_unter_spule", new = "on")
        self.listen_state(self.test_alarm, "input_boolean.test_alarm", new = "on")
        self.listen_event(self.button_wm_strom_an, "zha_event", device_ieee = "00:15:8d:00:04:0b:11:2f", command = "right_single")
    
    def eimer_hebeanlage_voll(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Eimer Hebeanlage voll - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            # alarm message via separate notify_when_status_matched app
            try:
                requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Alarm%20Eimer%20Hebeanlage%20ist%20voll&password=nopw", timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])
                            
    def wasser_boden_hebeanlage(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.turn_off("switch.waschmaschine")
            message = "Wasser auf dem Boden bei der Hebeanlage - habe die Waschmaschinen-Steckdose ausgeschalten!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            # alarm message via separate notify_when_status_matched app
            try:
                requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Alarm%20Wasser%20auf%20dem%20Boden%20bei%20der%20Hebeanlage&password=nopw", timeout=5)
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
            # alarm message via separate notify_when_status_matched app
            try:
                requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Achtung%20Hebeanlage%20hat%20keinen%20Strom&password=nopw", timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])

    def wasser_boden_spuelmaschine(self, entity, attribute, old, new, kwargs):
        if new != old:
            #self.turn_off("switch.waschmaschine")
            message = "Wasser auf dem Boden unter der Spüle oder Spülmaschine!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
            # alarm message via separate notify_when_status_matched app
            try:
                requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Alarm%20Wasser%20auf%20dem%20Boden%20bei%20der%20Sp%C3%BCle%20oder%20Sp%C3%BClmaschine&password=nopw", timeout=5)
            except:
            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])

    def test_alarm(self, entity, attribute, old, new, kwargs):
        if new != old:
            message = "Probealarm!"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
#            self.fire_event("custom_notify", message=message, target="telegram_ma")
            # alarm message via separate notify_when_status_matched app
#            try:
#                requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Probealarm&password=nopw", timeout=5)
#            except:
#            	pass
            fc = FritzCall(address=self.args["fritz_address"], password=self.args["fritz_pw"])
            fc.dial(self.args["phone_jo_handy"])

    def button_wm_strom_an(self,event_name,data,kwargs):
        self.turn_on("switch.waschmaschine")
        self.turn_on("switch.wasserabsperrventil")
        message = "Waschmaschine hat (wieder) Strom, Wasser ist wieder an"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
