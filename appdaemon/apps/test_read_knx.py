import appdaemon.plugins.hass.hassapi as hass

#
# Test app, reading a value from KNX Bus
# 

class test_read_knx(hass.Hass):

    def initialize(self):
        self.run_in(self.read_knx, 60)
        
    def read_knx(self,kwargs):
        self.call_service("knx_reader/read", address = "0/0/1")
        self.log("Triggered Read KNX")
        
