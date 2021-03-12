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
        self.reset_switch_entity = "switch.esp_sd_3_relais"
        self.reboot_delay_seconds = 5
        # presence
        self.timer_handle_wake = None
        self.timer_handle_sleep = None
        self.reboot_counter = 0
        self.error_counter = 0
        self.max_errors_before_reboot = 5
        self.max_reboots = 3
        self.listen_state(self.presence_on, "binary_sensor.anwesenheit_bildschirm", new = "on")
        self.listen_state(self.presence_off, "binary_sensor.anwesenheit_bildschirm", new = "off")
        if self.get_state("binary_sensor.anwesenheit_bildschirm") == "on":
            self.send_wake_command(None)
        else:
            self.send_sleep_command(None)
        # brightness
        current_brightness = self.get_state("sensor.helligkeit_kuche_pm")
        self.brightness_changed("sensor.helligkeit_kuche_pm", None, None, current_brightness, None)
        self.listen_state(self.brightness_changed, "sensor.helligkeit_kuche_pm")
        # reload page
#        self.run_in(self.send_reload_command, 60)


    def send_wake_command(self, kwargs):
        error = False
        try:
            requests.get("http://192.168.178.42:2323/?cmd=screenOn&password=nopw", timeout=5)
        except Exception as e:
            self.log("Error sending wake command to wallpanel via REST api. Error was {}".format(e))
            error = True
            self.requests_error()
        if not error:
            self.error_counter = 0
            self.reboot_counter = 0
        self.timer_handle_wake = self.run_in(self.send_wake_command,60)
        
    def send_sleep_command(self, kwargs):
        error = False
        try:
            requests.get("http://192.168.178.42:2323/?cmd=screenOff&password=nopw", timeout=5)
        except Exception as e:
            self.log("Error sending sleep command to wallpanel via REST api. Error was {}".format(e))
            error = True
            self.requests_error()
        if not error:
            self.error_counter = 0
            self.reboot_counter = 0
        self.timer_handle_sleep = self.run_in(self.send_sleep_command,60)
    
#    def send_reload_command(self, kwargs):
#        self.log("Sending reload command to wall panel")
#        try:
#            requests.get("", timeout=5)
#        except Exception as e:
#            self.log("Error sending reload command to wallpanel via REST api. Error was {}".format(e))

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
            if self.reboot_counter >= self.max_reboots:
                self.log("Already rebootet {} times. I think we lost this wall panel... Very sad".format(self.max_reboots))
            else:
                self.log("5 request errors. Will reboot wallpanel (reset switch)")
                self.turn_off(self.reset_switch_entity)
                self.run_in(self.turn_on_wallpanel, self.reboot_delay_seconds)
                self.fire_event("custom_notify", message="Habe den Bildschirm neu gestartet", target="telegram_jo")
                self.reboot_counter += 1

    def turn_on_wallpanel(self, kwargs):
        self.log("Booting Wallpanel")
        self.turn_on(self.reset_switch_entity)
        self.error_counter = 0
        
    def brightness_changed(self, entity, attributes, old, new, kwargs):
        self.log("adjusting wall panel brightness")
        try:
            brightness_float = float(new)
        except:
            self.log("Brightness not float, but: ".format(new))
            return
        if brightness_float <= 10:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=51&password=nopw", timeout=3)
        elif brightness_float <= 15:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=77&password=nopw", timeout=3)
        elif brightness_float <= 20:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=102&password=nopw", timeout=3)
        elif brightness_float <= 25:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=128&password=nopw", timeout=3)
        elif brightness_float <= 30:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=153&password=nopw", timeout=3)
        elif brightness_float <= 50:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=178&password=nopw", timeout=3)
        elif brightness_float <= 80:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=204&password=nopw", timeout=3)
        elif brightness_float <= 120:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=230&password=nopw", timeout=3)
        else:
            requests.get("http://192.168.178.42:2323/?cmd=setStringSetting&key=screenBrightness&value=255&password=nopw", timeout=3)
