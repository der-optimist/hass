import appdaemon.plugins.hass.hassapi as hass
from requests import get
import json
import datetime

#
# What it does:
#   - Load Birthday events into a HA variable (displayed in flex-table-card)
#   - Check "Reminders Calendar" for events and set a reminder
# What args it needs:
#   - token: a long lived token from HA
#

class calendar_and_reminders(hass.Hass):

    def initialize(self):
        # --- define variables ---
        self.ha_url = "http://192.168.1.30:8123"
        self.token = self.args["token"]
        self.days_birthdays = 31
        # --- birthdays to HASS variable ---
        time_check_birthdays = datetime.time(hour=0, minute=1, second=0)
        self.run_hourly(self.check_birthdays, time_check_birthdays)
        # --- set reminders triggered by google calendar events ---
        time_check_reminder = datetime.time(hour=0, minute=58, second=0)
        self.run_hourly(self.check_reminder, time_check_reminder)
        # --- do all the stuff at restarts ---
        self.listen_event(self.startup, "plugin_started")
        self.listen_event(self.startup, "appd_started")
        # --- initialize ---
        self.check_birthdays(None)
        self.check_reminder(None)
 
    def check_birthdays(self, kwargs):
        self.log("Checking Birthdays")
        start_dt = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00")
        end_dt = (datetime.datetime.now() + datetime.timedelta(days=self.days_birthdays)).strftime("%Y-%m-%dT00:00:00")
        summaries = []
        _dates = []
        weekdays = []
        _list = self.load_calendar("calendar.geburtstage_und_jahrestag",start_dt,end_dt)
        for element in _list:
            if "dateTime" in element["start"]:
                self.log("Birthday Calendar only supports all-day events. Found non-all-day event, but it will be ignored.")
            else:
                summary = ""
                _date = ""
                if "summary" in element and "date" in element["start"]:
                    summary = element["summary"]
                    summaries.append(summary)
                    _date = element["start"]["date"]
                    date_display = self.date_to_text(_date)
                    weekdays.append(date_display[0])
                    _dates.append(date_display[1])
                    self.log("{} {}: {}".format(date_display[0],date_display[1],summary))
                else:
                    self.log("No summary in event or no date in start of event - no idea what to do with that one, sorry")
        self.call_service("variable/set_variable",variable="birthdays",value="birthdays",attributes={"who": summaries, "when": _dates, "weekday": weekdays})

    def check_reminder(self, kwargs):
        self.log("Checking reminder events now")
        start_dt = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        end_dt = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        summaries = []
        start_dts = []
        end_dts = []
        _list = self.load_calendar("calendar.erinnerungen_bildschirm",start_dt,end_dt)
        for element in _list:
            self.log(element)
            summary = ""
            if "summary" in element:
                summary = element["summary"]
            start_dt = ""
            if "date" in element["start"]:
                start_dt = element["start"]["date"]
            elif "dateTime" in element["start"]:
                start_dt = element["start"]["dateTime"]
            end_dt = ""
            if "date" in element["end"]:
                end_dt = element["end"]["date"]
            elif "dateTime" in element["end"]:
                end_dt = (element["end"]["dateTime"]).split('+')[0]
            self.log("{} - {}: {} ".format(start_dt,end_dt,summary))
        self.utc_offset(None)

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

    def date_to_text(self, date_str):
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        _date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        days = (_date.date() - self.datetime().date()).days
        if days == 0:
            printtext = [" ","heute"]
        elif days == 1:
            printtext = [" ","morgen"]
        else:
            printtext = [_date.strftime('{}').format(weekdays[_date.weekday()]),_date.strftime('%d.%m. ({} T.)').format(days)]
        return printtext
        
    def utc_offset(self, kwargs):
        utc_offset_dt = datetime.datetime.now() - datetime.datetime.utcnow()
        utc_offset = utc_offset_dt.seconds//3600
        self.log(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        self.log(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
        self.log(utc_offset)
