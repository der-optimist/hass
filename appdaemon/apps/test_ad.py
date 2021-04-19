import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
#        return
        state = self.get_state("sensor.luftfeuchtigkeit_aussen")
        attributes = self.get_state("sensor.luftfeuchtigkeit_aussen", attribute="all")["attributes"]
        attributes["test"] = "Test-Attribut"
        self.set_state("sensor.luftfeuchtigkeit_aussen", state = state, attributes=attributes)
