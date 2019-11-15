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
        try:
            temp_ez = round(float(self.get_state("sensor.temp_esszimmer_taster")),1)
        except:
            temp_ez = "??"
        try:
            temp_aussen = round(float(self.get_state("sensor.temp_wetterstation")),1)
        except:
            temp_aussen = "??"
        try:
            wind = round(float(self.get_state("sensor.windgeschwindigkeit_wetterstation_kmh")))
        except:
            wind = "??"
        message="=== 🔥 Temperaturen ❄️ ===\n"\
                "Esszimmer: {} °C\n"\
                "Draussen: {} °C\n"\
                "Wind: {} km/h".format(temp_ez,temp_aussen,wind)
        self.fire_event("custom_notify", message=message, target="telegram_jo")
