import appdaemon.plugins.hass.hassapi as hass
from requests import get
import json

#
# testing the hass api
#

class calendar_and_reminders(hass.Hass):

    def initialize(self):
        self.load_cal()
        
    def load_cal(self):
        ha_url = "http://192.168.1.30:8123"
        token = self.args["token"]
        self.log(token)
        calendar = "calendar.geburtstage_und_jahrestag"
        start_date = "2019-02-05T00:00:00"
        end_date = "2019-07-04T00:00:00"
        headers = {'Authorization': "Bearer {}".format(token)}
        self.log("Try to load calendars")
        apiurl = "{}/api/calendars/{}?start={}Z&end={}Z".format(ha_url,calendar,start_date,end_date)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r)
        list = json.loads(r.text)
        for element in list:
          self.log(element)
          description = ""
          if "description" in element:
            description = element["description"]
          summary = ""
          if "summary" in element:
            summary = element["summary"]
          _date = ""
          if "date" in element["start"]:
            _date = element["start"]["date"]
          elif "dateTime" in element["start"]:
            _date = element["start"]["dateTime"]
          self.log("{}: {} ({})".format(_date,summary,description))
