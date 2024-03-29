import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

#
# App to handle the awesome pizza timer
#
# Args:
# 

class pizza_timer(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change, "input_number.pizza_timer_2")
#        self.url = "http://192.168.178.42:2971/api/command"
        self.timer_handle = None
        self.time_internal_state = 0
        if not float(self.get_state("input_number.pizza_timer_2")) == float(0):
            self.log("Pizza Timer nicht Null als ich gestartet wurde, werde jetzt weiter runter zaehlen")
            self.minute_abgelaufen(None)
        else:
            self.log("Pizza Timer ist Null als ich gestartet wurde, alles ruhig hier...")
    
    def state_change(self, entity, attributes, old, new, kwargs):
        self.log("State Change in Pizza Timer erkannt: {}".format(new))
        if round(float(new)) == 0:
            if self.time_internal_state == 0:
                self.log("Timer abgelaufen, werde jetzt an die Pizza erinnern")
                self.timer_handle = None
                self.remind_pizza(None)
            else:
                self.log("Timer wurde wohl manuell auf 0 gestellt, breche den Timer ab. Schade, keine Pizza!")
                self.time_internal_state = 0
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                    self.timer_handle = None
        else:
            if round(float(new)) == self.time_internal_state:
                self.log("Event wurde wohl durch mich selber ausgelöst weil eine Minute um ist, werde eine neue Minute timen...")
                self.timer_handle = self.run_in(self.minute_abgelaufen,60)
            else:
                self.log("Es wurde wohl eine neue Zeit eingestellt. Werde neuen Timer setzen")
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                self.time_internal_state = round(float(new))
                self.timer_handle = self.run_in(self.minute_abgelaufen,60)

    def minute_abgelaufen(self, kwargs):
        self.log("Eine Minute ist wohl um")
        self.time_internal_state = self.time_internal_state - 1
        old_state = round(float(self.get_state("input_number.pizza_timer_2")))
        self.set_value("input_number.pizza_timer_2", old_state - 1)

    def remind_pizza(self, kwargs):
        self.log("Pizza ist fertig")
        if self.get_state("media_player.kodi_wz_2") == "playing":
            self.call_service("notify/kodi_wz_2", title = "Pizza", message = "ist fertig", data = {"displaytime": 15000, "icon": "http://odroidxu4/sonstiges/pizza2.jpg"})
            self.call_service("kodi/call_method", entity_id = "media_player.kodi_wz_2", method = "Player.PlayPause", playerid = 1)
        else:
            self.fire_event("custom_notify", message="Pizza ist fertig, aber Kodi läuft gerade nicht - hoffentlich schaust du wenigstens aufs Handy...", target="telegram_jo")
            try:
                self.call_service("notify/kodi_wz_2", title = "Pizza", message = "ist fertig", data = {"displaytime": 15000, "icon": "http://odroidxu4/sonstiges/pizza2.jpg"})
            except Exception as e:
                self.log("Error sending pizza info to kodi. Error was {}".format(e))
        #self.call_service("mqtt/publish", topic = "wallpanel/mywallpanel/command", payload = "{\"speak\":\"Pizza ist fertig!\"}", qos = "2")
        # via REST api
        try:
            r = requests.get("http://192.168.178.42:2323/?cmd=textToSpeech&text=Pizza%20ist%20fertig%2E%20Lasst%20es%20euch%20schmecken&password=nopw", timeout=5)
            #self.log(r)
            #self.log(r.text)
        except Exception as e:
            self.log("Error sending speak command (pizza) to wallpanel via REST api. Error was {}".format(e))
