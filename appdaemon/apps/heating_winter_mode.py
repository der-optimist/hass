import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Set KNX Winter Switch According to HA Input Boolean 
#
# Args:
# - input_booloean_entity
# - ga (on which heating actor listenes for winter/summer info)
# 

class heating_winter_mode(hass.Hass):

    def initialize(self):
        # wait for KNX entities 
        self.ga = self.args["ga"]
        self.run_in(self.send_update,110)
        self.listen_state(self.input_changed, self.args["input_booloean_entity"])
        run_time = datetime.time(0, 38, 26) # more or less random timme
        self.run_hourly(self.send_update, run_time) # update every hour
    
    def send_update(self, kwargs):
        if self.get_state(self.args["input_booloean_entity"]) == "on":
            self.call_service("knx/send", address = self.ga, payload = 1)
        if self.get_state(self.args["input_booloean_entity"]) == "off":
            self.call_service("knx/send", address = self.ga, payload = 0)
    
    def input_changed(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.call_service("knx/send", address = self.ga, payload = 1)
        if new == "off":
            self.call_service("knx/send", address = self.ga, payload = 0)
