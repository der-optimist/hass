import appdaemon.plugins.hass.hassapi as hass
import xml.etree.ElementTree as ET
import requests, io
import json
import datetime

#
# What it does:
#
# What args it needs:
# 

class weather_and_astro(hass.Hass):

    def initialize(self):
        # --- DWD weather warnings ---
        self.url_tagesschau_100s = "https://www.tagesschau.de/export/video-podcast/webxl/tagesschau-in-100-sekunden_https/"
        #self.run_every(self.load_tagesschau_100s, datetime.datetime.now() + datetime.timedelta(seconds=3), 5 * 60) # update every 5 minutes
        self.load_tagesschau_100s(None)

    def load_tagesschau_100s(self, kwargs):
        try:
            r = requests.get(self.url_tagesschau_100s, allow_redirects=True)
        except:
            # catch connection error - r does not get a status code then
            self.log("Error while loading Tagesschau in 100s. Maybe connection problem")
            return
        if r.status_code == 200:
            xml = io.BytesIO(r.content)
            # Define Namespaces and load xml data
            namespaces = {
                'content': 'http://purl.org/rss/1.0/modules/content/', 
                'wfw': 'http://wellformedweb.org/CommentAPI/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'
            }
            tree = ET.parse(xml)
            root = tree.getroot()
            self.log(root)
            return
            
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

            # read warnings from xml
            for warning in root.findall('wfs:member', namespaces):
                event = warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text
                if (event != "FROST") and (event != "HITZE_off"):
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
