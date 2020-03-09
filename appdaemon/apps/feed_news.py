import appdaemon.plugins.hass.hassapi as hass
import xml.etree.ElementTree as ET
import requests, io
import datetime

#
# What it does:
# Check for new news video and write the new link to the html "player"
#
# What args it needs:
# 

class feed_news(hass.Hass):

    def initialize(self):
        # --- DWD weather warnings ---
        self.url_tagesschau_100s = "https://www.tagesschau.de/export/video-podcast/webxl/tagesschau-in-100-sekunden_https/"
        self.path_player_html = "/config/www/tagesschau/player_appdaemon.html"
        self.url_video = None
        self.run_every(self.load_tagesschau_100s, datetime.datetime.now() + datetime.timedelta(seconds=13), 10 * 60) # update every 10 minutes
        #self.load_tagesschau_100s(None)

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
            tree = ET.parse(xml)
            root = tree.getroot()
            link = root.findall('channel')[0].findall('item')[0].findall('enclosure')[0].get("url")
            if self.url_video != link:
                self.log("Jhu, neue Tagesschau!")
                self.url_video = link
                self.write_player_html()
            else:
                self.log("alte Tagesschau")

    def write_player_html(self):
        f = open(self.path_player_html, "w")
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<body>\n')
        f.write('<video width="95%" autoplay controls>\n')
        f.write('  <source src="{}" type="video/mp4">\n'.format(self.url_video))
        f.write('  Your browser does not support the video tag.\n')
        f.write('</video>\n')
        f.write('</body>\n')
        f.write('</html>\n')
        f.close()
