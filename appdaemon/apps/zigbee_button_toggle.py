import appdaemon.plugins.hass.hassapi as hass
#
# App does:
#  - Listen for single press of zigbee button and toggle an entity


class zigbee_button_toggle(hass.Hass):

    def initialize(self):
        self.zha_device_ieee = self.args["zha_device_ieee"]
        self.switch = self.args["toggle_entity"]
        self.listen_event(self.button_pressed, "zha_event", device_ieee = self.zha_device_ieee, command = "single")
        self.listen_event(self.button_pressed, "zha_event", device_ieee = self.zha_device_ieee, command = "double")
        
    def button_pressed(self,event_name,data,kwargs):
        self.toggle(self.switch)
        self.log("ZigBee Button Press => Will toggle now")
        self.log(data)

