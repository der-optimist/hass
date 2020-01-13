import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# What it does:
#   - Holds target temp. of "Wohnzimmer" and "Küche" same as "Esszimmer"
#     (only Esszimmer is controlled)
# What args it needs:
#   hard coded, as only needed once

class sync_target_temp_ez_wz_ku(hass.Hass):

    def initialize(self):
        self.check_interval_minutes = 5 # minutes
        for i in range(2,60,self.check_interval_minutes):
            self.run_hourly(self.check_sync_state, datetime.time(hour=0, minute=i, second=49))
        self.check_sync_state(None)

    def check_sync_state(self, kwargs):
        temp_ez = self.get_state("climate.esszimmer", attribute="temperature")
        temp_wz = self.get_state("climate.wohnzimmer", attribute="temperature")
        temp_ku = self.get_state("climate.kuche", attribute="temperature")
        
        if temp_wz != temp_ez:
            self.call_service("climate/set_temperature", entity_id = "climate.wohnzimmer", temperature = float(temp_ez))
            self.log("Target Temp. WZ differs from EZ. Set WZ to {} now".format(temp_ez))
        if temp_ku != temp_ez:
            self.call_service("climate/set_temperature", entity_id = "climate.kuche", temperature = float(temp_ez))
            self.log("Target Temp. KU differs from EZ. Set KU to {} now".format(temp_ez))
