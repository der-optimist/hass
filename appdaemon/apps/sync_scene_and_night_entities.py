import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Helper app, "hearing" for KNX scene commands and set state of HA-switches accordingly
#
# Args:
#  hard coded (yeah, bad style)
#


class sync_scene_and_night_entities(hass.Hass):

    def initialize(self):
        # listen for knx scene events
        self.listen_event(self.scene, event = "knx_event", address = "15/0/50")
        self.run_daily(self.reset_sleep_switches, datetime.time(9, 0, 0))
        # set "Bad OG Nachtmodus" if one of the children sleeps...
        self.listen_state(self.children_sleeping_changed, "binary_sensor.la_oder_le_schlafen")
        # set "Kater-Knopf" to off when majo_sleep turned off
        self.listen_state(self.reset_kater_knopf, "switch.majo_schlafen", new = "off")
        
    def scene(self,event_name,data,kwargs):
        self.log("KNX scene detected. data is:")
        self.log(data)
        if data["data"] == [0]:
            self.log("La geht ins Bett")
            self.turn_on("light.innr_rb_245_0b674403_level_on_off", brightness=255)
        elif data["data"] == [1]:
            self.log("Le geht ins Bett")
            self.turn_on("light.innr_rb_248_t_2192ebfe_level_light_color_on_off", brightness=255)
        #elif data["data"] == [3]:
        elif data["data"] == [3]:
            self.log("Fernseh-Szene")
        elif data["data"] == [4]:
            self.log("La steht auf")
            self.turn_off("switch.la_schlaft")
        elif data["data"] == [5]:
            self.log("Le steht auf")
            self.turn_off("switch.le_schlaft")
    
    def reset_sleep_switches(self,kwargs):
        # if "wake up button" was not used
        self.turn_off("switch.la_schlaft")
        self.turn_off("switch.le_schlaft")

    def children_sleeping_changed(self, entity, attribute, old, new, kwargs):
        if new == "on" and old != "on":
            self.turn_on("switch.bad_og_nachtmodus")
        elif new == "off" and old != "off":
            self.turn_off("switch.bad_og_nachtmodus")

    def reset_kater_knopf(self, entity, attribute, old, new, kwargs):
        if old != "off":
            self.turn_off("switch.kinder_schon_wach")
