import appdaemon.plugins.hass.hassapi as hass
#
# App does:
#  - Send notification on status change of aqara cube (testing)
#

class test_cube(hass.Hass):

    def initialize(self):
        self.listen_state(self.action, "sensor.0x00158d00027d4507_action")
        self.listen_state(self.side, "sensor.cube_1_side")
        
    def action(self, entity, attribute, old, new, kwargs):
        side = self.get_state("sensor.cube_1_side")
        self.fire_event("custom_notify", message="Cube Action changed: {} / Side zu dem Zeitpunkt: {}".format(new,side), target="telegram_jo")

    def side(self, entity, attribute, old, new, kwargs):
        self.fire_event("custom_notify", message="Cube Side changed: {}".format(new), target="telegram_jo")
