import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle the awesome pizza timer
#
# Args: 
# 

class pizza_timer(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change, "input_select.pizza_timer")
        self.timer_handle = None
    
    def state_change(self, entity, attributes, old, new, kwargs):
        self.log("State Change in Pizza Timer erkannt: {}".format(new))
        if new == "keine Pizza":
            self.log("Schade, keine Pizza")
            if self.timer_handle != None:
                self.cancel_timer(self.timer_handle)
                self.log("Es lief aber noch ein Timer, den hab ich jetzt abgebrochen")
        elif new == "Abbruch":
            if self.timer_handle == None:
                self.log("Pizza-Timer Abbruch angefragt, aber kein Timer vorhanden")
            else:
                self.cancel_timer(self.timer_handle)
                self.timer_handle = None
                self.log("Pizza-Timer abgebrochen")
                self.run_in(self.reset_pizza,2)
        else:
            if self.timer_handle != None:
                self.cancel_timer(self.timer_handle)
            self.starttime = datetime.datetime.now()
            delay_sec = int(new)
            self.timer_handle = self.run_in(self.remind_pizza,delay_sec)
            
    def remind_pizza(self, kwargs):
        self.log("Pizza ist fertig")
        self.call_service("notify/kodi_wz", title = "Pizza", message = "ist fertig", data = {"displaytime": 10000, "icon": "warning"})
        self.call_service("media_player/kodi_call_method", entity_id = "media_player.kodi", method = "Player.PlayPause", playerid = 0)
        self.select_option("input_select.pizza_timer", "keine Pizza")
    
    def reset_pizza(self, kwargs):
        self.log("Reset auf Keine Pizza")
        self.select_option("input_select.pizza_timer", "keine Pizza")
