import appdaemon.plugins.hass.hassapi as hass
import xml.etree.ElementTree as ET
import requests, io
import json

#
# What it does:
#   - Load Meteogram from meteograms.com and save locally (displayed via camera)
#   - Check DWD Weather Warnings
# What args it needs:
#   - meteograms_token: a token from meteograms.com
#   - dwd_warncell_id: as a string. find the ID here: 
#     https://www.dwd.de/DE/leistungen/opendata/help/warnungen/cap_warncellids_csv.csv
# 

class weather_and_astro(hass.Hass):

    def initialize(self):
        #self.meteograms_url = "https://nodeserver.cloud3squared.com/getMeteogram/%7B%22chartWidth%22%3A%22800%22%2C%22density%22%3A%221.2%22%2C%22appLocale%22%3A%22de%22%2C%22theme%22%3A%22dark-gradient%22%2C%22provider%22%3A%22dwd.de%22%2C%22hoursToDisplay%22%3A%2284%22%2C%22hoursAvailable%22%3A%2284%22%2C%22headerLocation%22%3A%22false%22%2C%22headerTemperature%22%3A%22false%22%2C%22headerMoonPhase%22%3A%22false%22%2C%22headerUpdateTime%22%3A%22false%22%2C%22precipitationSeries%22%3A%22expected%22%2C%22pressure%22%3A%22false%22%2C%22cloudLayers%22%3A%22false%22%2C%22windSpeed%22%3A%22true%22%2C%22windSpeedMinMaxLabels%22%3A%22false%22%2C%22windSpeedUnit%22%3A%22km%2Fh%22%2C%22windSpeedColor%22%3A%22%23ddc0c0c0%22%2C%22windSpeedAxisMin%22%3A%220%22%2C%22windSpeedAxisMax%22%3A%2240%22%2C%22windSpeedAxisScale%22%3A%22fixed%22%2C%22windArrows%22%3A%22false%22%7D"
        self.meteograms_base_url = "https://nodeserver.cloud3squared.com/getMeteogram/"
        self.meteograms_settings = {
            "chartWidth": "800",
            "density": "1.2",
            "appLocale": "de",
            "theme": "dark-gradient",
            "provider": "dwd.de",
            "hoursToDisplay": "84",
            "hoursAvailable": "84",
            "headerLocation": "false",
            "headerTemperature": "false",
            "headerMoonPhase": "false",
            "headerUpdateTime": "false",
            "precipitationSeries": "expected",
            "pressure": "false",
            "cloudLayers": "false",
            "windSpeed": "true",
            "windSpeedMinMaxLabels": "false",
            "windSpeedUnit": "km/h",
            "windSpeedColor": "#ddc0c0c0",
            "windSpeedAxisMin": "0",
            "windSpeedAxisMax": "40",
            "windSpeedAxisScale": "fixed",
            "windArrows": "false"
            }
        self.meteograms_url = self.meteograms_base_url + requests.utils.quote(json.dumps(self.meteograms_settings).replace(" ",""))
        self.meteogram_path = "/config/www/meteograms/meteogram.png"
        self.load_meteogram(None)
        
    def load_meteogram(self, kwargs):
        r = requests.get(self.meteograms_url, allow_redirects=True)
        self.log(r.status_code)
        if r.status_code == 200:
            open(self.meteogram_path, 'wb').write(r.content)
        else:
            self.log("downloading meteogram failed. http error.")

