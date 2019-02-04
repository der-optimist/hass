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
        ha_url = "http://192.168.1.30:8123/"
        token = self.args["token"]
        self.log(token)
        headers = {'Authorization': "Bearer {}".format(token)}
        self.log("Try to load calendars")
        apiurl = "{}/api/config".format(ha_url)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r.text)
