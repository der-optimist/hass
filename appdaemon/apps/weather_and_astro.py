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
        self.meteograms_base_url = "https://nodeserver.cloud3squared.com/getMeteogram/"
        self.meteograms_settings = {
            "token": "demo_6113b6da87fd72174bb3e5e0f5a",
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
        self.meteograms_url = self.meteograms_base_url + requests.utils.quote(json.dumps(self.meteograms_settings).replace(" ",""), safe='')
        self.meteogram_path = "/config/www/meteograms/meteogram.png"
        self.load_meteogram(None)
        
    def load_meteogram(self, kwargs):
        r = requests.get(self.meteograms_url, allow_redirects=True)
        self.log(r.status_code)
        if r.status_code == 200:
            open(self.meteogram_path, 'wb').write(r.content)
        else:
            self.log("downloading meteogram failed. http error.")

