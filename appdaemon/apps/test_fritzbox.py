import appdaemon.plugins.hass.hassapi as hass
from time import sleep
from fritzconnection import FritzConnection

#
# test
#
# Args: see initialize()
# 

class test_fritzbox(hass.Hass):

    def initialize(self):
        fc = FritzConnection(
                     address='192.168.178.1',
                     user=self.args["fritz_user"],
                     password=self.args["fritz_pw"])
        fc.call_action("X_VoIP1",
                       "X_AVM-DE_DialNumber",
                       arguments={
            "NewX_AVM-DE_PhoneNumber": self.args["phone_jo_handy"]})
        sleep(7)
        fc.call_action("X_VoIP1",
                       "X_AVM-DE_DialHangup")
    
    def initialize_delayed(self, kwargs):
       pass

    def update_notification(self, entity, attributes, old, new, kwargs):
        pass
