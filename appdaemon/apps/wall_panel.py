import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

#
# What it does:
#   - Send a wake command to the wall panel (during day time) for keeping it on
# 

class wall_panel(hass.Hass):

    def initialize(self):
        self.start_time = datetime.time(5,00)
        self.end_time = datetime.time(22,45)
        self.url = "http://192.168.178.26:2971/api/command"
        self.run_every(self.send_wake_command, datetime.datetime.now(), 5 * 60) # run every 5 minutes

    def send_wake_command(self, kwargs):
        if self.is_time_between(self.start_time, self.end_time):
            # via mqtt
            self.call_service("mqtt/publish", topic = "wallpanel/mywallpanel/command", payload = "{\"wake\":true,\"wakeTime\":610}", qos = "1")
            # via REST api
            data = {"wake": "true", "wakeTime": 610}
            headers = {"content-type": "application/json"}
            try:
                requests.post(self.url, headers=headers, json=data)
            except Exception as e:
                self.log("Error sending wake command to wallpanel via REST api. Error was {}".format(e))
        #else:
            #self.log("Nighttime - will let the panel sleep")
        
    def is_time_between(self, begin_time, end_time, check_time=None):
        # If check time is not given, default to current time
        check_time = check_time or datetime.datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else: # crosses midnight
            return check_time >= begin_time or check_time <= end_time
