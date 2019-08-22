import appdaemon.plugins.hass.hassapi as hass

#
# App does:
#  - Send command for reloading page to panel after a reboot
#
# Args:
# none

class reload_browser_page(hass.Hass):

    def initialize(self):
        # listen for new values
        self.run_in(self.send_reload_command, 120)
  
    def send_reload_command(self, kwargs):
        self.call_service("mqtt/publish", topic = "wallpanel/mywallpanel/command", payload = "{\"reload\":true}", qos = "2")
