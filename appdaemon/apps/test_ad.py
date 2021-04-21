import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
        #self.log(str(self.date())[8:10])
        #self.log(str(self.date())[5:10])
        #self.set_state("sensor.test_entity", state = 0.01, attributes = {"cost_test": "1.23"}, namespace = "ad_namespace")
        #self.log(self.get_state("sensor.test_entity", namespace = "ad_namespace"))
        self.log(self.get_state("sensor.stromverbrauch_verbrauch_gesamt", attribute="all", namespace = "ad_namespace"))
        self.log(self.get_state("sensor.stromverbrauch_waschmaschine", attribute="all", namespace = "ad_namespace"))
        return
