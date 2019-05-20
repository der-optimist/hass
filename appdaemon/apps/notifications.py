import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to notify when things happen:
#  - send temperatures in the morning
#
# Args:
#

class notifications(hass.Hass):

    def initialize(self):
        # --- send temps in the morning ---
        time_send_temps = datetime.time(4, 45, 00)
        self.run_daily(self.send_temps, time_send_temps)
        #self.send_temps(None) # for testing, send now
    
    def send_temps(self, kwargs):
        temp_wz = self.get_state("sensor.t_wz_ist_oh")
        temp_aussen = self.get_state("sensor.temp_owm")
        self.fire_event("custom_notify", message="===== Temperaturen =====\nWohnzimmer: {} °C\nDraussen: {} °C".format(temp_wz,temp_aussen), target="telegram_jo")
