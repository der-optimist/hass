import appdaemon.plugins.hass.hassapi as hass
from fritzconnection.lib.fritzcall import FritzCall

#
# test
#
# Args: see initialize()
# 

class test_fritzbox(hass.Hass):

    def initialize(self):
        fc = FritzCall(address='192.168.178.1', password=self.args["fritz_pw"])
        self.log(self.args["phone_jo_handy"])
        self.log(type(self.args["phone_jo_handy"]))
        fc.dial(self.args["phone_jo_handy"])

    
    def initialize_delayed(self, kwargs):
       pass

    def update_notification(self, entity, attributes, old, new, kwargs):
        pass
