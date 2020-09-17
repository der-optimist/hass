import appdaemon.plugins.hass.hassapi as hass
#import os
import subprocess
import datetime
import requests

#
# When there's no internet connection at the moment a telegram notification 
# should be sent, it gets lost. This app checks internet connection first
# and waits for it before sending the notification
#
# Args: no args required
# Usage: use e.g. self.fire_event("custom_notify", message="My Message", target="telegram_jo") in other app
#        target is the name defined in coniguration.yaml under notify:
#        or target can be "special_bot", then also "special_bot_api_key" and "special_bot_chat_id" must be provided. This
#        can be used to send messages via other telegram bots (e.g. special bot for urgent alarms)
# 

class custom_notify(hass.Hass):

    def initialize(self):
        self.listen_event(self.notification_received, event = "custom_notify")
        self.list_waiting_messages = []
        
    def notification_received(self,event_name,data,kwargs):
        # remove markdown commands
        data["message"] = data["message"].replace("_"," ").replace("*"," ")
        response_before = self.check_online_status()
        if response_before == 0:
        #if response_before == "test":
            self.log("google is up! will send message immediately")
            self.send_notification(data)
            response_after = self.check_online_status()
            if response_after == 0:
                self.log("google is still up, should be delivered")
            else:
                self.log("connection to google died during sending. will send later")
                if self.list_waiting_messages == []: # only trigger if this is the first waiting message. otherwise loop ist already running
                    self.run_in(self.send_waiting_notifications, 20)
                data["message"] = data["message"] + " \n(gespeicherte Nachricht vom " + datetime.datetime.now().strftime("%d.%m. %H:%M") + ")"
                self.list_waiting_messages.append(data)
                if len(self.list_waiting_messages) > 20:
                    del(self.list_waiting_messages[0])
        else:
            self.log("google is down! will send notification later")
            if self.list_waiting_messages == []: # only trigger if this is the first waiting message. otherwise loop ist already running
                self.run_in(self.send_waiting_notifications, 20)
            data["message"] = data["message"] + " \n(gespeicherte Nachricht vom " + datetime.datetime.now().strftime("%d.%m. %H:%M") + ")"
            self.list_waiting_messages.append(data)
            if len(self.list_waiting_messages) > 20:
                del(self.list_waiting_messages[0])
        
    def send_waiting_notifications(self, kwargs):
        response_before = self.check_online_status()
        if response_before == 0:
            self.log("google is up now! will send waiting notifications")
            for notification_data in self.list_waiting_messages:
                self.send_notification(notification_data)
            response_after = self.check_online_status()
            if response_after == 0:
                self.log("google is still up, should be delivered")
                self.list_waiting_messages = []
            else:
                self.log("connection to google died during sending. will send again")
                self.run_in(self.send_waiting_notifications, 20)
        else:
            self.run_in(self.send_waiting_notifications, 20)

    def send_notification(self, notification_data):
        if notification_data["target"] == "special_bot":
            if notification_data.get("special_bot_api_key", None) == None or notification_data.get("special_bot_chat_id", None) == None:
                self.log("When target is special bot, the special_bot_api_key and special_bot_chat_id must be provided!")
            else:
                url_send = 'https://api.telegram.org/bot' + str(notification_data["special_bot_api_key"]) + '/sendMessage?chat_id=' + str(notification_data["special_bot_chat_id"]) + '&parse_mode=Markdown&text=' + str(notification_data["message"])
                response = requests.get(url_send)
                self.log("http response special bot: {}".format(response))
        else:
            self.notify(notification_data["message"], name = notification_data["target"])

    def check_online_status(self):
        status = subprocess.call(['ping', '-c', '1', '-W', '2', 'google.com'],stdout=subprocess.DEVNULL)
        return status
