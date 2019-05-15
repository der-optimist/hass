import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to notify when things happen:
#  - arrived at work
#  - send temperatures in the morning
#
# Args:
# --- for "arrived at work" ---
# zone = Name of zone (only name of zone)
# device = tracked device (fully qualified => device_tracker.device_name)
#

class notifications(hass.Hass):

    def initialize(self):
        # --- notify work ---
        self.listen_state(self.arrived_at_work, self.args["device"], new = self.args["zone"])
        self.listen_state(self.left_work, self.args["device"], old = self.args["zone"])
        # --- send temps in the morning ---
        time_send_temps = datetime.time(4, 45, 00)
        self.run_daily(self.send_temps, time_send_temps)
        self.send_temps(None) # for testing, send now
        
    def arrived_at_work(self, entity, attribute, old, new, kwargs):
        self.log("Jo arrived at work")
        time_at_work = self.get_state("sensor.jo_at_work")
        self.log("Time at work: {}".format(time_at_work))
        if time_at_work == "0.0":
            self.fire_event("custom_notify", message="Angekommen", target="telegram_jo")
            #self.notify("Angekommen", name = "telegram_jo")

    def left_work(self, entity, attribute, old, new, kwargs):
        if new != self.args["zone"]:
            self.log("Jo left work")
            time_at_work_hm = self.get_state("sensor.jo_at_work", attribute="value")
            self.log("Time at work: {}".format(time_at_work_hm))
            self.fire_event("custom_notify", message="Feierabend! Reicht auch, nach {}".format(time_at_work_hm), target="telegram_jo")
    
    def send_temps(self, kwargs):
        temp_wz = self.get_state("sensor.t_wz_ist_oh")
        temp_aussen = self.get_state("sensor.temp_owm")
        self.fire_event("custom_notify", message="===== Temperaturen =====\nWohnzimmer: {} °C\nDraussen: {} °C".format(temp_wz,temp_aussen), target="telegram_jo")
