import appdaemon.plugins.hass.hassapi as hass
from requests import get
import json
import datetime
import variable

#
# Load Birthday events into a HASS variable
# Check "Reminders Calendar" for events and set a reminder
#

class calendar_and_reminders(hass.Hass):

    def initialize(self):
        # --- define variables ---
        self.ha_url = "http://192.168.1.30:8123"
        self.token = self.args["token"]
        self.days_birthdays = 60
        # --- birthdays to HASS variable ---
        time_check_birthdays = datetime.time(hour=0, minute=2, second=0)
        self.run_hourly(self.check_birthdays, time_check_birthdays)
        # --- do all the stuff at restarts ---
        self.listen_event(self.startup, "plugin_started")
        self.listen_event(self.startup, "appd_started")
        # --- initialize ---
        self.check_birthdays(None)
 
    def check_birthdays(self, kwargs):
        self.log("Checking Birthdays")
        start_dt = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00")
        end_dt = (datetime.datetime.now() + datetime.timedelta(days=self.days_birthdays)).strftime("%Y-%m-%dT00:00:00")
        summaries = []
        _dates = []
        _list = self.load_calendar("calendar.geburtstage_und_jahrestag",start_dt,end_dt)
        for element in _list:
            self.log(element)
            if "dateTime" in element["start"]:
                self.log("Birthday Calendar only supports all-day events. Found non-all-day event, but it will be ignored.")
            else:
                summary = ""
                _date = ""
                if "summary" in element and "date" in element["start"]:
                    summary = element["summary"]
                    summaries.append(summary)
                    _date = element["start"]["date"]
                    _dates.append(_date)
                    self.log("{}: {}".format(_date,summary))
                else:
                    self.log("No summary in event or no date in start of event - no idea what to do with that one, sorry")
        variable.set_variable("birthdays", "birthdays", {"who": summaries, "when": _dates}, None, None)


    def load_calendar(self,calendar,start_dt,end_dt):
        headers = {'Authorization': "Bearer {}".format(self.token)}
        self.log("Try to load calendar events")
        apiurl = "{}/api/calendars/{}?start={}Z&end={}Z".format(self.ha_url,calendar,start_dt,end_dt)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r)
        _list = json.loads(r.text)
        return _list

    def startup(self, event_name, data, kwargs):
        self.log("Startup detected")
        self.check_birthdays(None)
