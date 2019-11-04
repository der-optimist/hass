import appdaemon.plugins.hass.hassapi as hass
import requests

#
# What it does:
#   - Send a wake command to the wall panel for keeping it on (when presence)
#   - Send a reload command after wall panel disconnect or HA restart
# 

class wall_panel(hass.Hass):

    def initialize(self):
        # URL for REST api commands
        self.url = "http://192.168.178.26:2971/api/command"
        # presence
        self.listen_state(self.presence_on, "binary_sensor.anwesenheit_bildschirm", new = "on")
        self.listen_state(self.presence_off, "binary_sensor.anwesenheit_bildschirm", new = "off")
        if self.get_state("binary_sensor.anwesenheit_bildschirm") == "on":
            self.send_wake_command(None)
        # reload page
        self.listen_state(self.wp_online, "binary_sensor.ping_bildschirm", new = "on")
        #self.run_in(self.send_reload_command, 120) # auskommentiert wegen restart problem
        self.timer_handle = None

    def send_wake_command(self, kwargs):
        try:
            requests.post(self.url, json={"wake":"true","wakeTime":610}, timeout=5)
        except Exception as e:
            self.log("Error sending wake command to wallpanel via REST api. Error was {}".format(e))
        self.timer_handle = self.run_in(self.send_wake_command,60)
    
    def send_reload_command(self, kwargs):
        self.log("Sending reload command to wall panel")
        try:
            requests.post(self.url, json={"reload":"true"}, timeout=5)
        except Exception as e:
            self.log("Error sending reload command to wallpanel via REST api. Error was {}".format(e))

    def presence_on(self, entity, attributes, old, new, kwargs):
        self.log("Wall panel presence on. Will send periodic wake commands")
        self.send_wake_command(None)
    
    def presence_off(self, entity, attributes, old, new, kwargs):
        self.log("Wall panel presence off. Will cancel periodic wake commands")
        if self.timer_handle != None:
            self.cancel_timer(self.timer_handle)
            self.log("Canceled periodic wake commands")
        
    def wp_online(self, entity, attributes, old, new, kwargs):
        if old != "on":
            self.log("Wall Panel was offline, is online now. Will send reload command")
            self.send_reload_command(None)
