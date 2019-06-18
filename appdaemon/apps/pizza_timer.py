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
        elif new == "Abbruch":
            if self.timer_handle == None:
                self.log("Pizza-Timer Abbruch angefragt, aber kein Timer vorhanden")
            else:
                self.cancel_timer(self.timer_handle)
                self.timer_handle = None
                self.log("Pizza-Timer abgebrochen")
        else:
            if self.timer != None:
                self.cancel_timer(self.timer_handle)
            self.starttime = datetime.datetime.now()
            delay_sec = int(new)
            self.timer = self.run_in(self.remind_pizza,delay_sec)
            
    def remind_pizza(self, kwargs):
        self.log("Pizza ist fertig")
