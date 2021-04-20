import appdaemon.plugins.hass.hassapi as hass

class test_ad(hass.Hass):

    def initialize(self):
        #self.log(str(self.date())[8:10])
        #self.log(str(self.date())[5:10])
        self.log(self.list_namespaces())
        return
