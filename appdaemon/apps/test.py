import appdaemon.plugins.hass.hassapi as hass

#
# App to test input constraint
#
# Args: 
# 

class test(hass.Hass):

    def initialize(self):
        self.log("debug log",level="DEBUG")
        self.log("normal log")
    

