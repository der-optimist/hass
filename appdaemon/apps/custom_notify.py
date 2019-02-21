import appdaemon.plugins.hass.hassapi as hass

#
# When there's no internet connection at the moment a telegram notification 
# should be sent, it gets lost. This app checks internet connection first
# and waits for it before sending the notification
#
# Args: no args required
# 

class custom_notify(hass.Hass):

    def initialize(self):
        self.listen_event(self.send_notification, event = "custom_notify")
        self.list_waiting_messages = []
        
    def send_notification(self,event_name,data,kwargs):
        self.notify(data["message"], name = data["target"])
