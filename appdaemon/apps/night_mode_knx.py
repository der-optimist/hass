import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Helper app, defining night mode "switches" for knx (used e.g. in "Glastaster")
#
# Args:
#  hard coded (yeah, bad style)
#


class night_mode_knx(hass.Hass):

    def initialize(self):
        # Kinderzimmer
        self.run_daily(self.kinderzimmer_nacht, datetime.time(18, 0, 0))
        self.run_daily(self.kinderzimmer_tag, datetime.time(8, 0, 0))
        
    def kinderzimmer_nacht(self, kwargs):
        self.set_state("switch.nachtmodus_kinderzimmer'", state = "on")
    
    def kinderzimmer_tag(self, kwargs):
        self.set_state("switch.nachtmodus_kinderzimmer'", state = "off")
