import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
        all_ha_lights = self.get_state("light")
        self.log(all_ha_lights)
