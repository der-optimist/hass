import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
        return
        all_ha_lights = self.get_state("light")
        for light in all_ha_lights.keys():
            self.log(light)
