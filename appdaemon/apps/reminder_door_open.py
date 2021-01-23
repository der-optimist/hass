import appdaemon.plugins.hass.hassapi as hass

#
# App to demind if door left open
#
# Args: see initialize()
# 

class reminder_door_open(hass.Hass):

    def initialize(self):
        # Args
        self.binary_sensor_reminder = self.args["binary_sensor_reminder"]
        self.reminder_switch_name = self.args["reminder_switch_name"]
        self.text_reminder_switch = self.args["text_reminder_switch"]
        
        self.attributes_reminder_switch = {"icon": "mdi:door-open", "friendly_name": self.text_reminder_switch}
        if self.get_state(self.binary_sensor_reminder) == "on":
            self.set_state(self.reminder_switch_name, state = "on", attributes = self.attributes_reminder_switch)
            self.log("startup: door is open")
        else:
            self.set_state(self.reminder_switch_name, state = "off", attributes = self.attributes_reminder_switch)
            self.log("startup: door is closed")
        
        self.listen_state(self.remind, self.binary_sensor_reminder)

    def remind(self, entity, attributes, old, new, kwargs):
        if new == "on":
            self.set_state(self.reminder_switch_name, state = "on", attributes = self.attributes_reminder_switch)
            self.log("door open")
        elif new == "off":
            self.set_state(self.reminder_switch_name, state = "off", attributes = self.attributes_reminder_switch)
            self.log("door closed")
