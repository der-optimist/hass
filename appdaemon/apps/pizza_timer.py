import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle the awesome pizza timer
#
# Args: 
# 

class pizza_timer(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change, "input_number.pizza_timer_2")
        self.timer_handle = None
        self.time_internal_state = 0
    
    def state_change(self, entity, attributes, old, new, kwargs):
        self.log("State Change in Pizza Timer erkannt: {}".format(new))
        if new == 0:
            if self.time_internal_state == 0:
                self.log("Timer abgelaufen, werde jetzt an die Pizza erinnern")
                self.remind_pizza(None)
            else:
                self.log("Timer wurde wohl manuell auf 0 gestellt, breche den Timer ab. Schade, keine Pizza!")
                self.time_internal_state = 0
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
        else:
            if new == self.time_internal_state:
                self.log("Event wurde wohl durch mich selber ausgelöst weil eine Minute um ist, werde eine neue Minute timen...")
                self.timer_handle = self.run_in(self.minute_abgelaufen,60)
            else:
                self.log("Es wurde wohl eine neue Zeit eingestellt. Werde neuen Timer setzen")
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                self.time_internal_state = new
                self.timer_handle = self.run_in(self.minute_abgelaufen,60)

    def minute_abgelaufen(self, kwargs):
        self.log("Eine Minute ist wohl um")
        self.time_internal_state = self.time_internal_state - 1
        old_state = self.get_state("input_number.pizza_timer_2")
        self.input_number.select_value("input_number.pizza_timer_2", old_state - 1)

    def remind_pizza(self, kwargs):
        self.log("Pizza ist fertig")
        #self.call_service("notify/kodi_wz", title = "Pizza", message = "ist fertig", data = {"displaytime": 15000, "icon": "http://rp3/pizza_kodi.jpg"})
        #self.call_service("media_player/kodi_call_method", entity_id = "media_player.kodi", method = "Player.GetActivePlayers")
        #self.call_service("media_player/kodi_call_method", entity_id = "media_player.kodi", method = "Player.PlayPause", playerid = 1)
