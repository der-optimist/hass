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
        self.icon_reminder_standard = "/local/icons/garbage/tonne_gelb_blink.svg"
        # --- birthdays to HASS variable ---
        time_check_birthdays = datetime.time(hour=0, minute=1, second=0)
        self.run_hourly(self.check_birthdays, time_check_birthdays)
        # --- set reminders triggered by google calendar events ---
        self.check_reminder_repeat_minutes = 15
        for i in range(0,60,self.check_reminder_repeat_minutes):
            self.run_hourly(self.check_reminder, datetime.time(hour=0, minute=i, second=10))
        self.check_reminder_repeat_counter = 0
        # --- do all the stuff at restarts ---
        self.listen_event(self.startup, "plugin_started")
        self.listen_event(self.startup, "appd_started")
        # --- initialize ---
        self.check_birthdays(None)
 
    def check_birthdays(self, kwargs):
        self.log("Checking Birthdays")
        utc_offset = self.utc_offset(None)
        start_dt = (datetime.datetime.now() - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
        end_dt = (datetime.datetime.now() + datetime.timedelta(days=self.days_birthdays) - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
        summaries = []
        _dates = []
        weekdays = []
        _list = self.load_calendar("calendar.geburtstage_und_jahrestag",start_dt,end_dt)
        if _list == "error":
            self.log("received http error - will retry later")
            self.run_in(self.check_birthdays, 600)
        else:
            for element in _list:
                if "dateTime" in element["start"]:
                    self.log("Birthday Calendar only supports all-day events. Found event that is not all-day, it will be ignored.")
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
        #self.log("Checking reminder events now")
        utc_offset = self.utc_offset(None)
        start_dt = (datetime.datetime.now() - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
        end_dt = (datetime.datetime.now() + datetime.timedelta(minutes=(self.check_reminder_repeat_minutes - 1)) - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
        summaries = []
        start_dts = []
        end_dts = []
        _list = self.load_calendar("calendar.erinnerungen_bildschirm",start_dt,end_dt)
        if _list == "error":
            if self.check_reminder_repeat_counter < (self.check_reminder_repeat_minutes - 2):
                self.check_reminder_repeat_counter += 1
                self.log("received http error - will retry later. This will be repeat No. {}".format(self.check_reminder_repeat_counter))
                self.run_in(self.check_reminder, 60)
            else:
                self.log("Max repeat cycles of check_rminder reached. Next check will be the normal one...")
                self.check_reminder_repeat_counter = 0
        else:
            self.check_reminder_repeat_counter = 0
            for element in _list:
                #self.log(element)
                summary = ""
                if "summary" in element:
                    summary = element["summary"]
                start_dt = ""
                if "date" in element["start"]:
                    start_dt = element["start"]["date"] + 'T00:00:00'
                elif "dateTime" in element["start"]:
                    start_dt = (element["start"]["dateTime"]).split('+')[0]
                #self.log("{}: {} ".format(start_dt,summary))
                event_start_dt = datetime.datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%S")
                last_minute_dt = datetime.datetime.now().replace(second=0) - datetime.timedelta(seconds=1)
                end_check_interval_dt = last_minute_dt + datetime.timedelta(minutes=(self.check_reminder_repeat_minutes - 1 - self.check_reminder_repeat_counter), seconds=59)
                #self.log(last_minute_dt.strftime("%Y-%m-%dT%H:%M:%S"))
                #self.log(event_start_dt.strftime("%Y-%m-%dT%H:%M:%S"))
                #self.log(end_check_interval_dt.strftime("%Y-%m-%dT%H:%M:%S"))
                if event_start_dt >= last_minute_dt and event_start_dt < end_check_interval_dt:
                    self.log("{} sollte ich als reminder setzen!".format(summary))
                    reminder_name = "self.switch_reminder_" + summary.replace(" ","").replace(".","").replace("!","").replace("?","").replace(".","")
                    self.set_state(reminder_name, state = "on", attributes={"entity_picture":self.icon_reminder_standard, "fiendly_name": summary})
                else:
                    self.log("{} startete wohl nicht in diesem Interval".format(summary))

    def load_calendar(self,calendar,start_dt,end_dt):
        headers = {'Authorization': "Bearer {}".format(self.token)}
        #self.log("Try to load calendar events")
        apiurl = "{}/api/calendars/{}?start={}Z&end={}Z".format(self.ha_url,calendar,start_dt,end_dt)
        self.log("ha_config: url is {}".format(apiurl))
        r = get(apiurl, headers=headers, verify=False)
        self.log(r)
        self.log(r.text)
        if r.ok:
            if "summary" in r.text:
                resp = json.loads(r.text) # List
            else:
        	    resp = []
        else:
            self.log("http error while loading calendars")
            resp = "error"
        return resp

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
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
        #self.log("utc offset: {}d {}sec".format(utc_offset_dt.days, utc_offset_dt.seconds))
        return utc_offset_dt
