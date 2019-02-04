import appdaemon.plugins.hass.hassapi as hass
#import aiohttp
from requests import get

#
# testing the hass api
#

class test_cal(hass.Hass):

    def initialize(self):
        self.load_cal()
        
    def load_cal(self):
        #conn = aiohttp.TCPConnector()
        #self.session = aiohttp.ClientSession(connector=conn)
        ha_url = "http://hassio/homeassistant"
        token = self.args["token"]
        headers = {'Authorization': "Bearer {}".format(token)}
        self.log("Try to load calendars")
        apiurl = "{}/api/config".format(ha_url)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r.text)
