import appdaemon.plugins.hass.hassapi as hass
import os
import datetime

#
# When there's no internet connection at the moment a telegram notification 
# should be sent, it gets lost. This app checks internet connection first
# and waits for it before sending the notification
#
# Args: no args required
# Usage: use e.g. self.fire_event("custom_notify", message="My Message", target="telegram_jo") in other app
#        target is the name defined in coniguration.yaml under notify:
# 

class custom_notify(hass.Hass):

    def initialize(self):
        self.listen_event(self.send_notification, event = "custom_notify")
        self.list_waiting_messages = []
        
    def send_notification(self,event_name,data,kwargs):
        # remove markdown commands
        message = date["message"].replace("_"," ").replace("*"," ")
        response_before = os.system("ping -c 1 -w2 google.com")
        if response_before == 0:
        #if response_before == "test":
            self.log("google is up! will send message immediately")
            self.notify(message, name = data["target"])
            response_after = os.system("ping -c 1 -w2 google.com")
            if response_after == 0:
                self.log("google is still up, should be delivered")
            else:
                self.log("connection to google died during sending. will send later")
                if self.list_waiting_messages == []: # only trigger if this is the first waiting message. otherwise loop ist already running
                    self.run_in(self.send_waiting_notifications, 60)
                self.list_waiting_messages.append({"message":message, "target":data["target"], "dt":datetime.datetime.now().strftime("%d.%m. %H:%M")})
        else:
            self.log("google is down! will send notification later")
            if self.list_waiting_messages == []: # only trigger if this is the first waiting message. otherwise loop ist already running
                self.run_in(self.send_waiting_notifications, 60)
            self.list_waiting_messages.append({"message":message, "target":data["target"], "dt":datetime.datetime.now().strftime("%d.%m. %H:%M")})
        
    def send_waiting_notifications(self, kwargs):
        response_before = os.system("ping -c 1 -w2 google.com")
        if response_before == 0:
            self.log("google is up now! will send waiting notifications")
            for notification in self.list_waiting_messages:
                message_modified = notification["message"] + " \n(gespeicherte Nachricht vom " + notification["dt"] + ")"
                self.notify(message_modified, name = notification["target"])
            response_after = os.system("ping -c 1 -w2 google.com")
            if response_after == 0:
                self.log("google is still up, should be delivered")
                self.list_waiting_messages = []
            else:
                self.log("connection to google died during sending. will send again")
                self.run_in(self.send_waiting_notifications, 60)
        else:
            self.run_in(self.send_waiting_notifications, 60)
