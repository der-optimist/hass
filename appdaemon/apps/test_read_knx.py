import appdaemon.plugins.hass.hassapi as hass

#
# Test app, reading a value from KNX Bus
# 

class test_read_knx(hass.Hass):

    def initialize(self):
        self.listen_event(self.read_knx, event = "custom_read_knx")
        
    def read_knx(self,event_name,data,kwargs):
        self.log("Received a Custom Read KNX event")
        
