import appdaemon.plugins.hass.hassapi as hass
import xml.etree.ElementTree as ET
import requests, io
import json
import datetime

#
# What it does:
#   - Load Meteogram from meteograms.com and save locally (displayed via camera)
#   - Check DWD Weather Warnings and create HA sensors
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
            "token": self.args["token_meteograms"],
            "chartWidth": "900",
            "placeName": self.args["home_town"],
            "longPlaceName": self.args["home_town"],
            "latitude": str(self.args["home_latitude"]),
            "longitude": str(self.args["home_longitude"]),
            "countryCode": "DE",
            "appLocale": "de",
            "theme": "dark-gradient",
            "provider": "dwd.de",
            "hoursToDisplay": "162",
            "hoursAvailable": "162",
            "headerLocation": "false",
            "headerTemperature": "false",
            "headerMoonPhase": "false",
            "headerUpdateTime": "false",
            "precipitationSeries": "expected",
            "precipitationAxisMin": "0",
            "precipitationAxisMax": "40",
            "precipitationAxisScale": "fixed",
            "pressure": "false",
            "cloudLayers": "false",
            "windSpeed": "true",
            "windSpeedMinMaxLabels": "false",
            "windSpeedUnit": "km/h",
            "windSpeedColor": "#ddc0c0c0",
            "windSpeedAxisMin": "0",
            "windSpeedAxisMax": "40",
            "windSpeedAxisScale": "fixed",
            "windArrows": "false",
            "compressionQuality": "90.0"
            }
        self.url_meteograms = self.base_url_meteograms + requests.utils.quote(json.dumps(self.settings_meteograms).replace(" ",""), safe='')
        self.path_meteogram = "/config/www/meteograms/meteogram.png"
        time_load_meteogram = datetime.time(5, 00, 20)
        self.run_daily(self.load_meteogram, time_load_meteogram)
        self.load_meteogram(None) # for testing
        # --- DWD weather warnings ---
        self.dwd_warncell_id = self.args["dwd_warncell_id"]
        #self.dwd_warncell_id = 816054000 #Suhl, for testing
        self.url_dwd_warnings = "https://maps.dwd.de/geoserver/dwd/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=dwd:Warnungen_Gemeinden&CQL_FILTER=WARNCELLID%20IN%20(%27{}%27)".format(self.dwd_warncell_id)
        self.run_every(self.load_dwd_warnings, datetime.datetime.now(), 5 * 60)

    def load_meteogram(self, kwargs):
        try:
            r = requests.get(self.url_meteograms, allow_redirects=True)
        except:
            self.log("Error while loading meteogram. Maybe connection problem")
            self.run_in(self.load_meteogram, 120)
            return
        if r.status_code == 200:
            open(self.path_meteogram, 'wb').write(r.content)
        else:
            self.log("downloading meteogram failed. http error {}".format(r.status_code))
            self.run_in(self.load_meteogram, 120)

    def minutely_check_dwd_warnings(self, kwargs):
        if (self.counter_dwd_warnings % self.minutes_dwd_warnings) == 0:
            self.load_dwd_warnings(None)
        self.counter_dwd_warnings += 1

    def load_dwd_warnings(self, kwargs):
        self.curr_utc_offset = self.utc_offset(None)
        try:
            r = requests.get(self.url_dwd_warnings, allow_redirects=True)
        except:
            self.log("Error while loading DWD Warnings. Maybe connection problem")
            return
        #self.log("http status code dwd warnings: {}".format(r.status_code))
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
            Start_readable = []
            End_readable = []
            EC_Groups = []
            Parametervalues = []
            Descriptions = []
            Severities_dict = {'Extreme': 4, 'Severe': 3, 'Moderate': 2, 'Minor': 1}

            # read warnings from xml
            for warning in root.findall('wfs:member', namespaces):
                event = warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text
                if (event != "FROST_TEST") and (event != "HITZE"):
                    Events.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text)
                    Severities.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:SEVERITY', namespaces)[0].text)
                    Times_onset.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:ONSET', namespaces)[0].text)
                    start_dt = datetime.datetime.strptime(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:ONSET', namespaces)[0].text, "%Y-%m-%dT%H:%M:%SZ")
                    Start_readable.append(self.datetime_readable(start_dt))
                    Times_expires.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EXPIRES', namespaces)[0].text)
                    end_dt = datetime.datetime.strptime(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EXPIRES', namespaces)[0].text, "%Y-%m-%dT%H:%M:%SZ")
                    End_readable.append(self.datetime_readable(end_dt))
                    EC_Groups.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EC_GROUP', namespaces)[0].text)
                    try:
                        Parametervalues.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:PARAMATERVALUE', namespaces)[0].text)
                    except IndexError:
                        Parametervalues.append("")
                    Descriptions.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:DESCRIPTION', namespaces)[0].text)
            Severities_sortable = [Severities_dict.get(item,item) for item in Severities]

            # write into one list and sort by severity and start time
            data = []
            for i in range(len(Events)):
                data.append([Severities_sortable[i], Times_onset[i], Times_expires[i], Start_readable[i], End_readable[i], Events[i], Severities[i], EC_Groups[i], Parametervalues[i], Descriptions[i]])
            data_sorted = sorted(data, key=lambda x: (-x[0], x[1]))
            list_of_active_sensors = []
            for warning in data_sorted:
                event = warning[5]
                attributes = {"friendly_name": event, "von": warning[3], "bis": warning[4], "Beschreibung": warning[9], "Stärke (0-4)": warning[0]}
                sensor_name = "sensor.dwd_warn_" + event.lower() + "_" + warning[1].replace("-","_").replace(":","_").replace("T","").replace("Z","")
                self.set_state(sensor_name, state = event, attributes = attributes)
                list_of_active_sensors.append(sensor_name)
            all_ha_sensors = self.get_state("sensor")
            self.log(all_ha_sensors)
        else:
            self.log("downloading dwd warnings failed. http error {}".format(r.status_code))

    def datetime_readable(self, dt):
        dt_local_naive_str = (dt + self.curr_utc_offset).strftime("%Y-%m-%dT%H:%M:%S")
        hour_str = dt_local_naive_str[11:13]
        date_readable_str = self.date_to_text(dt_local_naive_str[0:10])
        dt_readable_str = date_readable_str + " " + hour_str + " Uhr"
        #self.log(dt_readable_str)
        return dt_readable_str
    
    def utc_offset(self, kwargs):
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
        #self.log("utc offset: {}d {}sec".format(utc_offset_dt.days, utc_offset_dt.seconds))
        return utc_offset_dt
    
    def date_to_text(self, date_str):
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        _date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        days = (_date.date() - self.datetime().date()).days
        if days == 0:
            printtext = "heute"
        elif days == 1:
            printtext = "morgen"
        else:
            printtext = _date.strftime('{}, %d.%m.').format(weekdays[_date.weekday()])
        return printtext
