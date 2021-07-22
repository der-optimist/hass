import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

#
# Helper app, "hearing" for KNX scene commands and set state of HA-switches accordingly
#
# Args:
#  hard coded (yeah, bad style)
#


class sync_scene_and_night_entities(hass.Hass):

    def initialize(self):
        # listen for knx scene events
        self.listen_event(self.scene, event = "knx_event", destination = "15/0/50")
        # toggle HA switches via KNX button
        self.listen_event(self.toggle_poweroutlet_phone_ma, event = "knx_event", destination = "0/3/20")
        self.listen_event(self.toggle_poweroutlet_phone_jo, event = "knx_event", destination = "0/3/40")
        self.run_daily(self.reset_sleep_switches, datetime.time(9, 0, 0))
        # set "Bad OG Nachtmodus" if one of the children sleeps...
        self.listen_state(self.children_sleeping_changed, "binary_sensor.la_oder_le_schlafen")
        # set "Kater-Knopf" to off when majo_sleep turned off
        self.listen_state(self.reset_kater_knopf, "switch.majo_schlafen", new = "off")
        # Alles-Lüften handeln und Panels Treppe OG aus wenn Lüften Le oder La
        self.listen_state(self.lueften_alles_start, "switch.luften_alles", new = "on", old = "off")
        self.listen_state(self.lueften_alles_ende, "switch.luften_alles", new = "off", old = "on")
        self.listen_state(self.panels_treppe_og_aus, "switch.luften_le", new = "on", old = "off")
        self.listen_state(self.panels_treppe_og_aus, "switch.luften_la", new = "on", old = "off")
        # turn luften_alles off when all single ones are off
        self.listen_state(self.turn_off_alles_luften, "switch.luften_ez", new = "off", old = "on")
        self.listen_state(self.turn_off_alles_luften, "switch.luften_sz", new = "off", old = "on")
        self.listen_state(self.turn_off_alles_luften, "switch.luften_le", new = "off", old = "on")
        self.listen_state(self.turn_off_alles_luften, "switch.luften_la", new = "off", old = "on")
        
    def scene(self,event_name,data,kwargs):
        self.log("KNX scene detected. data is:")
        self.log(data)
        if data["data"] == [0]:
            self.log("La geht ins Bett")
            self.turn_on("light.innr_e14_ww_stehlampe_lara_level_on_off", brightness=255)
        elif data["data"] == [1]:
            self.log("Le geht ins Bett")
            self.turn_on("light.innr_e14_tw_stehlampe_lea_level_light_color_on_off", brightness=255)
        #elif data["data"] == [3]:
        elif data["data"] == [3]:
            self.log("Fernseh-Szene")
        elif data["data"] == [4]:
            self.log("La steht auf")
            self.turn_off("switch.la_schlaft")
        elif data["data"] == [5]:
            self.log("Le steht auf")
            self.turn_off("switch.le_schlaft")
        elif data["data"] == [21]:
            self.log("Lueftung hochschalten")
            # setze Laufzeit Stoßlüftung auf 30 Minuten
            self.call_service("modbus/write_register", address = 1103, unit = 1, value = 30, hub = "lueftungsanlage")
            time.sleep(1)
            # starte Stoßlüftung
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 4, hub = "lueftungsanlage")
        elif data["data"] == [22]:
            self.log("Lueftung Automatik")
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 1, hub = "lueftungsanlage")
            
    def toggle_poweroutlet_phone_ma(self,event_name,data,kwargs):
        self.log("Toggle poweroutlet phone ma")
        self.toggle("switch.shellyswitch25_10521c45de0b_relay_0")
        
    def toggle_poweroutlet_phone_jo(self,event_name,data,kwargs):
        self.log("Toggle poweroutlet phone jo")
        self.toggle("switch.shellyswitch25_10521c45de0b_relay_1")
    
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

    # Lüften
    def lueften_alles_start(self, entity, attribute, old, new, kwargs):
        self.run_in(self.lueften_ez_start, 1)
        self.run_in(self.lueften_sz_start, 6)
        self.run_in(self.lueften_la_start, 11)
        self.run_in(self.lueften_le_start, 16)
        
    def lueften_alles_ende(self, entity, attribute, old, new, kwargs):
        self.run_in(self.lueften_ez_ende, 1)
        self.run_in(self.lueften_sz_ende, 6)
        self.run_in(self.lueften_la_ende, 11)
        self.run_in(self.lueften_le_ende, 16)
    
    def lueften_ez_start(self,kwargs):
        self.turn_on("switch.luften_ez")
    def lueften_ez_ende(self,kwargs):
        self.turn_off("switch.luften_ez")
    def lueften_sz_start(self,kwargs):
        self.turn_on("switch.luften_sz")
    def lueften_sz_ende(self,kwargs):
        self.turn_off("switch.luften_sz")
    def lueften_le_start(self,kwargs):
        self.turn_on("switch.luften_le")
    def lueften_le_ende(self,kwargs):
        self.turn_off("switch.luften_le")
    def lueften_la_start(self,kwargs):
        self.turn_on("switch.luften_la")
    def lueften_la_ende(self,kwargs):
        self.turn_off("switch.luften_la")

    def turn_off_alles_luften(self, entity, attribute, old, new, kwargs):
        if self.get_state("switch.luften_ez") == "off" and self.get_state("switch.luften_sz") == "off" and self.get_state("switch.luften_le") == "off" and self.get_state("switch.luften_la") == "off":
            self.turn_off("switch.luften_alles")
        
    def panels_treppe_og_aus(self, entity, attribute, old, new, kwargs):
        self.turn_off("light.panels_treppe_og")
