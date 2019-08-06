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
#   - home_town: Name of home town, for meteograms.com
#   - home_latitude: for meteograms.com
#   - home_longitude: for meteograms.com
# 

class weather_and_astro(hass.Hass):

    def initialize(self):
        # --- meteogram ---
        self.base_url_meteograms = "https://nodeserver.cloud3squared.com/getMeteogram/"
        self.settings_meteograms = {
            "token": self.args["token_meteograms"],
            "chartWidth": "1350",
            "chartHeight": "360",
            "placeName": self.args["home_town"],
            "longPlaceName": self.args["home_town"],
            "latitude": str(self.args["home_latitude"]),
            "longitude": str(self.args["home_longitude"]),
            "countryCode": "DE",
            "appLocale": "de",
            "theme": "dark-gradient",
            "daylightBandsWeekendColorDiff": "true",
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
        time_load_meteogram = datetime.time(5, 00, 20) # update time for meteogram
        self.run_daily(self.load_meteogram, time_load_meteogram)
        self.load_meteogram(None) # for testing, load now
        # --- DWD weather warnings ---
        self.dwd_warncell_id = self.args["dwd_warncell_id"]
        #self.dwd_warncell_id = 809180117 #Garmisch, for testing
        self.url_dwd_warnings = "https://maps.dwd.de/geoserver/dwd/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=dwd:Warnungen_Gemeinden&CQL_FILTER=WARNCELLID%20IN%20(%27{}%27)".format(self.dwd_warncell_id)
        self.run_every(self.load_dwd_warnings, datetime.datetime.now(), 5 * 60) # update every 5 minutes
        self.just_started = True # prevent repeated notifications after a restart

    def load_meteogram(self, kwargs):
        try:
            r = requests.get(self.url_meteograms, allow_redirects=True)
        except:
            # catch connection error - r does not get a status code then
            self.log("Error while loading meteogram. Maybe connection problem")
            # try again in 2 minutes
            self.run_in(self.load_meteogram, 120)
            return
        if r.status_code == 200:
            open(self.path_meteogram, 'wb').write(r.content)
        else:
            self.log("downloading meteogram failed. http error {}".format(r.status_code))
            # try again in 2 minutes
            self.run_in(self.load_meteogram, 120)

    def load_dwd_warnings(self, kwargs):
        self.curr_utc_offset = self.utc_offset(None)
        try:
            r = requests.get(self.url_dwd_warnings, allow_redirects=True)
        except:
            # catch connection error - r does not get a status code then
            self.log("Error while loading DWD Warnings. Maybe connection problem")
            return
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
            Icons_dict = {
                1: "/local/icons/reminders/exclamation_mark_yellow.svg",
                2: "/local/icons/reminders/exclamation_mark_orange.svg",
                3: "/local/icons/reminders/exclamation_mark_red.svg",
                4: "/local/icons/reminders/exclamation_mark_purple.svg",
            }

            # read warnings from xml
            for warning in root.findall('wfs:member', namespaces):
                event = warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text
                if (event != "FROST_off") and (event != "HITZE_off"):
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
            
            # create a sensor for each warning
            list_of_active_sensors = []
            for warning in data_sorted:
                event = warning[5]
                if event == "UV-INDEX":
                    event = "UV-Warnung"
                start_end_readable = warning[3] + " bis " + warning[4]
                icon = Icons_dict.get(warning[0],"/local/icons/reminders/exclamation_mark_blink.svg")
                attributes = {"friendly_name": event, "entity_picture": icon, "Dauer": start_end_readable, "Beschreibung": warning[9], "Gefahr (0-4)": warning[0]}
                sensor_name = "sensor.dwd_warn_" + event.lower().replace(" ","_").replace("-","_").replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("/","").replace("__","_") + "_" + warning[1].replace("-","_").replace(":","_").replace("T","_").replace("Z","")
                if (self.get_state(sensor_name) != start_end_readable) or (self.get_state(sensor_name, attribute = "Gefahr (0-4)") != warning[0]):
                    self.log("Sensor {} scheint neu zu sein".format(sensor_name))
                    if warning[0] >= 1: # Severity
                        if self.just_started: # prevent repeated notifications after a restart
                            self.log("Warnung gefunden, aber just-started flag erkannt. Sende deshalb keine Benachrichtigung")
                        else:
                            if event == "UV-Warnung":
                                self.fire_event("custom_notify", message="Warnung - {}:\n{}\nGefahr (0-4): {}".format(start_end_readable,"Hohe UV-Werte",warning[0]), target="telegram_jo")
                            else:
                                self.fire_event("custom_notify", message="Warnung - {}:\n{}\nGefahr (0-4): {}".format(start_end_readable,warning[9],warning[0]), target="telegram_jo")
                #else:
                    #self.log("Sensor {} ist wohl nicht neu".format(sensor_name))
                self.set_state(sensor_name, state = start_end_readable, attributes = attributes)
                list_of_active_sensors.append(sensor_name)
            
            # set outdated sensors to "off"
            all_ha_sensors = self.get_state("sensor")
            for sensor, value in all_ha_sensors.items():
                if sensor.startswith("sensor.dwd_warn_") and (sensor not in list_of_active_sensors) and (value["state"] != "off"):
                    self.set_state(sensor, state = "off")
            # First notification after startup should be passed...
            self.just_started = False
                    
        else:
            # log http error. no second try here, as update will be done in a few minutes anyway
            self.log("downloading dwd warnings failed. http error {}".format(r.status_code))

    def datetime_readable(self, dt):
        dt_local_naive_str = (dt + self.curr_utc_offset).strftime("%Y-%m-%dT%H:%M:%S")
        if dt_local_naive_str[11] == "0":
            hour_str = dt_local_naive_str[12:13]
        else:
            hour_str = dt_local_naive_str[11:13]
        date_readable_str = self.date_to_text(dt_local_naive_str[0:10])
        dt_readable_str = date_readable_str + " " + hour_str + " Uhr"
        return dt_readable_str
    
    def utc_offset(self, kwargs):
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
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
