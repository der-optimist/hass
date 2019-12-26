import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when things happen:
#  - motion
#
# Args:
#

class treppenhausalarm(hass.Hass):

    def initialize(self):
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
    
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        self.log(old)
        self.log(new)
        if new == "on" and old != "on":
            message="Achtung, Bewegung! ({})".format(entity)
            self.fire_event("custom_notify", message=message, target="telegram_jo")
