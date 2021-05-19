import appdaemon.plugins.hass.hassapi as hass

#
# App to store config variables, that are used by more than one AD app
# 

class global_vars(hass.Hass):

    def initialize(self):
        self.log("Global vars app loaded")
