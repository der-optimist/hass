import appdaemon.plugins.hass.hassapi as hass
#
# App does:
#  - Listen for single press of zigbee button and toggle sleep mode
#  - Listen for single press of zigbee button and toggle light (10%) 
# Args:
#  - sensor_entity
#  - sleep_mode_switch_entity
#  - light_entity


class gz_zigbee_button(hass.Hass):

    def initialize(self):
        self.zha_device_ieee = self.args["zha_device_ieee"]
        self.switch = self.args["sleep_mode_switch_entity"]
        self.light = self.args["light_entity"]
        self.listen_event(self.button_pressed, "zha_event", device_ieee = self.zha_device_ieee)
#        self.listen_event(self.button_single, "zha_event", device_ieee = self.zha_device_ieee, command = "single")
#        self.listen_event(self.button_double, "zha_event", device_ieee = self.zha_device_ieee, command = "double")
        
    def button_pressed(self,event_name,data,kwargs):
        self.toggle(self.switch)
        self.log("ZigBee Button Press => Will toggle sleep mode switch")

#        if new == "double" and new != old:
#            if self.get_state(self.light) == "on":
#                self.turn_off(self.light)
#            else:
#                self.turn_on(self.light, brightness = 25)
