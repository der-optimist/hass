import appdaemon.plugins.hass.hassapi as hass
from requests import get

#
# testing the hass api
#

class test_cal(hass.Hass):

    def initialize(self):
        self.load_cal()
        
    def load_cal(self):
        ha_url = "http://192.168.1.30:8123"
        token = self.args["token"]
        calendar = "calendar.geburtstage_und_jahrestag"
        start_date = "2019-02-04T00:00:00"
        end_date = "2019-04-04T00:00:00"
        headers = {'Authorization': "Bearer {}".format(token)}
        self.log("Try to load calendars")
        apiurl = "{}/api/calendars/{}?start={}Z&end={}Z".format(ha_url,calendar,start_date,end_date)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r.json())
