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
        self.listen_event(self.scene, event = "knx_event", destination = "15/0/50")

        
    def scene(self,event_name,data,kwargs):
        if data["data"] == [21]:
            self.log("Lueftung hochschalten")
            # setze Laufzeit Stoßlüftung auf 30 Minuten
            self.call_service("modbus/write_register", address = 1103, unit = 1, value = 30, hub = "lueftungsanlage")
            time.sleep(1)
            # starte Stoßlüftung
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 4, hub = "lueftungsanlage")
        elif data["data"] == [22]:
            self.log("Lueftung Automatik")
            self.call_service("modbus/write_register", address = 1161, unit = 1, value = 1, hub = "lueftungsanlage")
            
