import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# What it does:
#   - Send a day or night command to KNX at specific time
# 

class day_night(hass.Hass):

    def initialize(self):
        self.day_time = datetime.time(7,30)
        self.night_time = datetime.time(18,30)
        self.address = "7/3/3"
        self.run_daily(self.send_day, self.start_time)
        self.run_daily(self.send_night, self.start_time)

    def send_day(self, kwargs):
        self.log("Daytime")
        self.call_service("knx/send", address = self.address, payload = 1)
    
    def send_night(self, kwargs):
        self.log("Nighttime")
        self.call_service("knx/send", address = self.address, payload = 0)
        
    def is_time_between(self, begin_time, end_time, check_time=None):
        # If check time is not given, default to current time
        check_time = check_time or datetime.datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else: # crosses midnight
            return check_time >= begin_time or check_time <= end_time
