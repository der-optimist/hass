import appdaemon.plugins.hass.hassapi as hass
import requests

#
# What it does:
#   - Send a wake command to the wall panel for keeping it on (when presence)
#   - Send a sleep command to the wall panel for keeping it off (when no presence)
#   - Hard Reset the device if not reachable
#   - Send a reload command after HA restart
# 

class wall_panel(hass.Hass):

    def initialize(self):
        # URL for REST api commands
        self.url = "http://192.168.178.42:2971/api/command"
        self.reset_switch_entity = "switch.esp_sd_3_relais"
        self.reboot_delay_seconds = 5
        # presence
        self.timer_handle_wake = None
        self.timer_handle_sleep = None
        self.error_counter = 0
        self.max_errors_before_reboot = 5
        self.listen_state(self.presence_on, "binary_sensor.anwesenheit_bildschirm", new = "on")
        self.listen_state(self.presence_off, "binary_sensor.anwesenheit_bildschirm", new = "off")
        if self.get_state("binary_sensor.anwesenheit_bildschirm") == "on":
            self.send_wake_command(None)
        else:
            self.send_sleep_command(None)
        # reload page
        self.run_in(self.send_reload_command, 60)


    def send_wake_command(self, kwargs):
        error = False
        try:
            requests.post(self.url, json={"wake":"true","wakeTime":610}, timeout=5)
        except Exception as e:
            self.log("Error sending wake command to wallpanel via REST api. Error was {}".format(e))
            error = True
            self.requests_error()
        if not error:
            self.error_counter = 0
        self.timer_handle_wake = self.run_in(self.send_wake_command,60)
        
    def send_sleep_command(self, kwargs):
        error = False
        try:
            requests.post(self.url, json={"wake":"false"}, timeout=5)
        except Exception as e:
            self.log("Error sending sleep command to wallpanel via REST api. Error was {}".format(e))
            error = True
        if not error:
            self.error_counter = 0
        self.timer_handle_sleep = self.run_in(self.send_sleep_command,60)
    
    def send_reload_command(self, kwargs):
        self.log("Sending reload command to wall panel")
        try:
            requests.post(self.url, json={"reload":"true"}, timeout=5)
        except Exception as e:
            self.log("Error sending reload command to wallpanel via REST api. Error was {}".format(e))

    def presence_on(self, entity, attributes, old, new, kwargs):
        #self.log("Wall panel presence on. Will send periodic wake commands")
        if self.timer_handle_sleep != None:
            self.cancel_timer(self.timer_handle_sleep)
        self.send_wake_command(None)
    
    def presence_off(self, entity, attributes, old, new, kwargs):
        #self.log("Wall panel presence off. Will cancel periodic wake commands")
        if self.timer_handle_wake != None:
            self.cancel_timer(self.timer_handle_wake)
        self.send_sleep_command(None)

    def requests_error(self):
        self.log("Processing requests error")
        self.error_counter += 1
        if self.error_counter >= self.max_errors_before_reboot:
            self.log("5 request errors. Will reboot wallpanel (reset switch)")
            self.turn_off(self.reset_switch_entity)
            self.run_in(self.turn_on_wallpanel, self.reboot_delay_seconds)
            self.fire_event("custom_notify", message="Habe den Bildschirm neu gestartet", target="telegram_jo")

    def turn_on_wallpanel(self, kwargs):
        self.log("Booting Wallpanel")
        self.turn_on(self.reset_switch_entity)
        self.error_counter = 0
