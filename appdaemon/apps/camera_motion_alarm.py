import appdaemon.plugins.hass.hassapi as hass
from shutil import copyfile

#
# App to handle motion alarm from IP camera (image uploaded to FTP)
#
# Args: 
# 

class camera_motion_alarm(hass.Hass):

    def initialize(self):
        self.listen_event(self.folder_watcher_event, "folder_watcher", event_type = 'created')
        self.camera_image_path = "/config/www/camera_abstellraum/last_motion.jpg"
#        copyfile('/share/abstellraum/20200203/images/A20020308260010.jpg', self.camera_image_path)
    
    def folder_watcher_event(self, event_name, data, kwargs):
        self.log(event_name)
        self.log(data)
        image_path = data["path"]
        self.log(image_path)
        self.call_service('notify/telegram_jo',
                          message="Bewegung",
                          data= {'photo': {'file': image_path, 'caption': 'Abstellraum'}})
        copyfile(image_path, self.camera_image_path)
