import appdaemon.plugins.hass.hassapi as hass
import xml.etree.ElementTree as ET
import requests, io
import json

#
# What it does:
#   - Load Meteogram from meteograms.com and save locally (displayed via camera)
#   - Check DWD Weather Warnings
# What args it needs:
#   - token_meteograms: a token from meteograms.com
#   - dwd_warncell_id: as a string. find the ID here: 
#     https://www.dwd.de/DE/leistungen/opendata/help/warnungen/cap_warncellids_csv.csv
# 

class weather_and_astro(hass.Hass):

    def initialize(self):
        # --- meteogram ---
        self.base_url_meteograms = "https://nodeserver.cloud3squared.com/getMeteogram/"
        self.settings_meteograms = {
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
        self.url_meteograms = self.base_url_meteograms + requests.utils.quote(json.dumps(self.settings_meteograms).replace(" ",""), safe='')
        self.path_meteogram = "/config/www/meteograms/meteogram.png"
        self.load_meteogram(None)
        # --- DWD weather warnings ---
        self.url_dwd_warnings = "https://maps.dwd.de/geoserver/dwd/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=dwd:Warnungen_Gemeinden&CQL_FILTER=WARNCELLID%20IN%20(%27{}%27)".format(self.args["dwd_warncell_id"])
        self.load_dwd_warnings(None)

    def load_meteogram(self, kwargs):
        r = requests.get(self.url_meteograms, allow_redirects=True)
        self.log(r.status_code)
        if r.status_code == 200:
            open(self.path_meteogram, 'wb').write(r.content)
        else:
            self.log("downloading meteogram failed. http error {}".format(r.status_code))

    def load_dwd_warnings(self, kwargs):
        r = requests.get(self.url_dwd_warnings, allow_redirects=True)
        self.log(r.status_code)
        if r.status_code == 200:
            xml = io.BytesIO(r.content)
            # Define Namespaces and load xml data
            namespaces = {
                'xs': 'http://www.w3.org/2001/XMLSchema', 
                'dwd': 'http://www.dwd.de',
                'wfs': 'http://www.opengis.net/wfs/2.0',
                'gml': 'http://www.opengis.net/gml/3.2',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }
            tree = ET.parse(xml)
            root = tree.getroot()

            # initialize vars
            Events = []
            Severities = []
            Times_onset = []
            Times_expires = []
            EC_Groups = []
            Parametervalues = []
            Severities_dict = {'Extreme': 1, 'Severe': 2, 'Moderate': 3, 'Minor': 4}

            # read warnings from xml
            for warning in root.findall('wfs:member', namespaces):
                event = warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text
                if (event != "FROST") and (event != "HITZE"):
                    Events.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text)
                    Severities.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:SEVERITY', namespaces)[0].text)
                    Times_onset.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:ONSET', namespaces)[0].text)
                    Times_expires.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EXPIRES', namespaces)[0].text)
                    EC_Groups.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EC_GROUP', namespaces)[0].text)
                    Parametervalues.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:PARAMATERVALUE', namespaces)[0].text)
            Severities_sortable = [Severities_dict.get(item,item) for item in Severities]

            # write into one list and sort by severity and start time
            data = []
            for i in range(len(Events)):
                data.append([Severities_sortable[i], Times_onset[i], Times_expires[i], Events[i], Severities[i], EC_Groups[i], Parametervalues[i]])
            data_sorted = sorted(data, key=lambda x: (x[0], x[1]))
            self.log(data_sorted)
        else:
            self.log("downloading dwd warnings failed. http error {}".format(r.status_code))
