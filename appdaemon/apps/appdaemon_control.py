import appdaemon.plugins.hass.hassapi as hass

#
# 

class appdaemon_control(hass.Hass):

    def initialize(self):
        self.listen_state(self.production_mode_changed,"input_boolean.appdaemon_production_mode")
        self.run_in(self.initialize_delayed,170)

    def appdaemon_production_mode(self, entity, attribute, old, new, kwargs):
        if new == "on" and old != new:
            self.call_service("production_mode/set", mode=True, namespace="appdaemon")
        elif new == "off" and old != new:
            self.call_service("production_mode/set", mode=False, namespace="appdaemon")
        else:
            self.log("I do not know what to do with new value {} for input_boolean.appdaemon_production_mode".format(new))
    
    def initialize_delayed(self, kwargs):
        status_input_boolean = self.get_status("input_boolean.appdaemon_production_mode")
        if status_input_boolean == "on":
            self.call_service("production_mode/set", mode=True, namespace="appdaemon")
        elif status_input_boolean == "off":
            self.call_service("production_mode/set", mode=False, namespace="appdaemon")
        else:
            self.log("I do not know what to do with status {} for input_boolean.appdaemon_production_mode".format(status_input_boolean))
