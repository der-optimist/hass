import appdaemon.plugins.hass.hassapi as hass

#
# App to test "reliable notification" app
# 
#

class test_fire_notification(hass.Hass):

    def initialize(self):
        self.fire_event("custom_notify", message="My Test Message 4", target="telegram_jo")
        self.fire_event("custom_notify", message="My Test Message 5", target="telegram_jo")
