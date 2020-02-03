import appdaemon.plugins.hass.hassapi as hass

#
# App to handle motion alarm from IP camera (image uploaded to FTP)
#
# Args: 
# 

class camera_motion_alarm(hass.Hass):

    def initialize(self):
        self.listen_event(self.folder_watcher_event, "folder_watcher")
    
    def folder_watcher_event(self, event_name, data, kwargs):
        self.log(event_name)
        self.log(data)
        self.log(kwargs)
