import appdaemon.plugins.hass.hassapi as hass
import time

#
# Helper app handling ventilation tasks
#
# Args:
#  hard coded (yeah, bad style)
#


class ventilation(hass.Hass):

    def initialize(self):
        # listen for knx scene events
        #self.listen_event(self.scene, event = "knx_event", destination = "15/0/50")
        # gäste
        self.listen_state(self.gaeste_start, "input_boolean.gaeste_abends", new = "on", old = "off")
        self.listen_state(self.gaeste_end, "input_boolean.gaeste_abends", new = "off", old = "on")

        
    def scene(self,event_name,data,kwargs):
        if data["data"] == [21]:
            self.log("Szene - Lueftung hochschalten auf Stosslueftung")
            # setze Laufzeit Stoßlüftung auf 30 Minuten
            self.call_service("modbus/write_register", address = 1103, unit = 1, value = 30, hub = "lueftungsanlage")
            time.sleep(1)
            # starte Stoßlüftung
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 4, hub = "lueftungsanlage")
        elif data["data"] == [22]:
            self.log("Szene - Lueftung Automatik")
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 1, hub = "lueftungsanlage")
    
    def gaeste_start(self, entity, attribute, old, new, kwargs):
            self.log("Gaeste Start - Lueftung auf Party")
            # setze Laufzeit Party auf 8 Stunden (Maximum)
            self.call_service("modbus/write_register", address = 1104, unit = 1, value = 8, hub = "lueftungsanlage")
            time.sleep(1)
            # starte Party Modus
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 3, hub = "lueftungsanlage")
            
    def gaeste_end(self, entity, attribute, old, new, kwargs):
            self.log("Gaeste Ende - Lueftung Automatik")
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 1, hub = "lueftungsanlage")
