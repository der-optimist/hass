import appdaemon.plugins.hass.hassapi as hass
from requests import get
import json
import datetime

#
# What it does:
#   - Load Birthday events into a HA variable (displayed in flex-table-card)
#   - Check "Reminders Calendar" for events and set a reminder
# What args it needs:
#   - token: a long lived token from HA
# 

class calendar_and_reminders(hass.Hass):

    def initialize(self):
        self.meteogras_url = "https://nodeserver.cloud3squared.com/getMeteogram/%7B%22chartWidth%22%3A%22800%22%2C%22density%22%3A%221.2%22%2C%22appLocale%22%3A%22de%22%2C%22theme%22%3A%22dark-gradient%22%2C%22provider%22%3A%22dwd.de%22%2C%22hoursToDisplay%22%3A%2284%22%2C%22hoursAvailable%22%3A%2284%22%2C%22headerLocation%22%3A%22false%22%2C%22headerTemperature%22%3A%22false%22%2C%22headerMoonPhase%22%3A%22false%22%2C%22headerUpdateTime%22%3A%22false%22%2C%22precipitationSeries%22%3A%22expected%22%2C%22pressure%22%3A%22false%22%2C%22cloudLayers%22%3A%22false%22%2C%22windSpeed%22%3A%22true%22%2C%22windSpeedMinMaxLabels%22%3A%22false%22%2C%22windSpeedUnit%22%3A%22km%2Fh%22%2C%22windSpeedColor%22%3A%22%23ddc0c0c0%22%2C%22windSpeedAxisMin%22%3A%220%22%2C%22windSpeedAxisMax%22%3A%2240%22%2C%22windSpeedAxisScale%22%3A%22fixed%22%2C%22windArrows%22%3A%22false%22%7D"
        
