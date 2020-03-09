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

class feed_news(hass.Hass):

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
        self.log(r.status_code)
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
            link = root.findall('channel')[0].findall('item')[0]
            self.log(link)
