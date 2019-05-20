import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App does:
#  - Set status of devices based on zones
#  - Send notifications based on zones (for testing)
#
# Args:
# --- for "arrived/left work" ---
# zone = Name of zone (only name of zone)
# device = tracked device (fully qualified => device_tracker.device_name)
# name_jo = Name of jo
#

class locations(hass.Hass):

    def initialize(self):
        self.listen_state(self.arrived_at_work, self.args["device"], new = self.args["zone"])
        self.listen_state(self.left_work, self.args["device"], old = self.args["zone"])
        self.listen_state(self.arrived_at_home, self.args["device"], new = "home")
        self.listen_state(self.left_home, self.args["device"], old = "home")
        self.name_jo = self.args["name_jo"]
        self.sensor_location_jo = "sensor.location_jo"
        
    def arrived_at_work(self, entity, attribute, old, new, kwargs):
        self.log("Jo arrived at work")
        self.set_state(self.sensor_location_jo, state = "Bei der Arbeit", attributes={"entity_picture":"/local/icons/locations/manager.svg", "friendly_name": self.name_jo})
        time_at_work = self.get_state("sensor.jo_at_work")
        self.log("Time at work: {}".format(time_at_work))
        if time_at_work == "0.0":
            self.fire_event("custom_notify", message="Bei der Arbeit angekommen", target="telegram_jo")

    def left_work(self, entity, attribute, old, new, kwargs):
        if new != self.args["zone"]:
            self.set_state(self.sensor_location_jo, state = "Unterwegs", attributes={"entity_picture":"/local/icons/locations/destination.svg", "friendly_name": self.name_jo})
            self.log("Jo left work")
            time_at_work_hm = self.get_state("sensor.jo_at_work", attribute="value")
            self.log("Time at work: {}".format(time_at_work_hm))
            self.fire_event("custom_notify", message="Feierabend! Reicht auch, nach {}".format(time_at_work_hm), target="telegram_jo")
    
    def arrived_at_home(self, entity, attribute, old, new, kwargs):
        self.set_state(self.sensor_location_jo, state = "Unterwegs", attributes={"entity_picture":"/local/icons/locations/at_home.svg", "friendly_name": self.name_jo})
        if old != "home":
            self.log("Jo arrived at home")
            self.fire_event("custom_notify", message="Zu Hause angekommen", target="telegram_jo")
        
    def left_home(self, entity, attribute, old, new, kwargs):
        if new != "home":
            self.set_state(self.sensor_location_jo, state = "Unterwegs", attributes={"entity_picture":"/local/icons/locations/destination.svg", "friendly_name": self.name_jo})
            self.log("Jo left home")
            self.fire_event("custom_notify", message="Weg von zu Hause", target="telegram_jo")
