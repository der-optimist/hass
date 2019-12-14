import appdaemon.plugins.hass.hassapi as hass

#
# Helper app for dimming a zigbee (or another) light via KNX 
#
# Args:
# - light_entity
# - steps (list of dimming values)
# - command_ga_dim (1 = up / 0 = down)
# - command_ga_switch (1 = 100% / 0 = off)
#


class knx_dim_funk(hass.Hass):

    def initialize(self):
        self.light = self.args["light_entity"]
        self.steps = self.args["steps"]
        # listen for knx events
        self.listen_event(self.received_dim_command, event = "knx_event", address = self.args["command_ga_dim"])
        self.listen_event(self.received_switch_command, event = "knx_event", address = self.args["command_ga_switch"])
        
    def received_dim_command(self,event_name,data,kwargs):
        self.log("KNX command for step-dimming detected. Light is: {}. Data is:".format(self.light))
        self.log(data)
        try:
            self.current_brightness = self.byte_to_pct(self.get_state(self.light, attribute="brightness"))
        except:
            self.current_brightness = float(0)
        if data["data"] == 0:
            next_step = self.find_next_lower_value()
        elif data["data"] == 1:
            next_step = self.find_next_higher_value()
        self.turn_on(self.light,brightness=self.pct_to_byte(next_step))
        else:
            self.log("Not 0 and not 1? command_ga_dim should be binary! Please check config")

    def received_switch_command(self,event_name,data,kwargs):
        self.log("KNX command for swtiching detected. Light is: {}. Data is:".format(self.light))
        self.log(data)
        if data["data"] == 0:
            self.turn_off(self.light)
        elif data["data"] == 1:
            self.turn_on(self.light,brightness=self.pct_to_byte(100))
        else:
            self.log("Not 0 and not 1? command_ga_dim should be binary! Please check config")
    
    def find_next_higher_value(self):
        for step in sorted(self.steps):
            higher_value = step
            if step > self.current_brightness:
                break
        return higher_value

    def find_next_lower_value(self):
        for step in sorted(self.steps, reverse=True):
            lower_value = step
            if step < self.current_brightness:
                break
        return lower_value

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
