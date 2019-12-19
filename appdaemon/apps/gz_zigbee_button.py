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
        self.sensor = self.args["sensor_entity"]
        self.switch = self.args["sleep_mode_switch_entity"]
        self.light = self.args["light_entity"]
        self.listen_state(self.sensor_state_changed, self.sensor, attribute = "click")
        
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        if new == "single" and new != old:
            self.toggle(self.switch)
            self.log("ZigBee Button Press single => Will toggle sleep mode switch")
        if new == "double" and new != old:
            if self.get_state(self.light) == "on":
                self.turn_off(self.light)
            else:
                self.turn_on(self.light, brightness = 25)
