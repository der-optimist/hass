import appdaemon.plugins.hass.hassapi as hass
from requests import get

#
# testing the hass api
#

class test_cal(hass.Hass):

    def initialize(self):
        self.load_cal()
        
    def load_cal(self):+
        self.log(self.ha_url)
        self.log("Try to load calendars")
        token = self.args["token"]
        auth = 'Bearer ' + token
        self.log(auth)
        url = 'http://hassio:8123/api/config'
        headers = {
            'Authorization': auth,
            'content-type': 'application/json',
        }
        response = get(url, headers=headers, verify=False)
        self.log(response.text)
