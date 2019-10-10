import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Helper app, "hearing" for KNX scene commands and set state of HA-switches accordingly
#
# Args:
#  hard coded (yeah, bad style)
#


class sync_scene_entities(hass.Hass):

    def initialize(self):
        # listen for knx scene events
        self.listen_event(self.scene, event = "knx_event", address = "15/0/50")
        self.run_daily(self.reset_sleep_switches, datetime.time(9, 0, 0))
        
    def scene(self,event_name,data,kwargs):
        self.log("KNX scene detected. data is:")
        self.log(data)
        if data == 1:
            self.log("La geht ins Bett")
            self.set_state("switch.la_schlaft", state = "on")
        elif data == 2:
            self.log("Le geht ins Bett")
            self.set_state("switch.le_schlaft", state = "on")
        elif data == 5:
            self.log("La steht auf")
            self.set_state("switch.la_schlaft", state = "off")
        elif data == 6:
            self.log("Le steht auf")
            self.set_state("switch.le_schlaft", state = "off")
    
    def reset_sleep_switches(self,event_name,data,kwargs):
        # if "wake up button" was not used
        self.set_state("switch.la_schlaft", state = "off")
        self.set_state("switch.le_schlaft", state = "off")
