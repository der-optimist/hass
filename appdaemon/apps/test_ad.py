import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
        self.log(self.date())
        return
