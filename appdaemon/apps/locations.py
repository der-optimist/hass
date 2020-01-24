import appdaemon.plugins.hass.hassapi as hass

#
# App does:
#  - Set sensor for display, based on location info from tasker
#  - Send notifications based on location changes (for testing)
#
# Args:
# name_jo = Name of jo
#

class locations(hass.Hass):

    def initialize(self):
        self.sensor_location_jo = "sensor.location_jo" # where to show the information
        self.input_location_jo_roh = "input_text.location_jo_roh" # where tasker sends the value to
        self.name_jo = self.args["name_jo"]
        # listen state
        self.listen_state(self.location_changed, self.input_location_jo_roh)
        # show the current location immediately after restart
        current_value = self.get_state(self.input_location_jo_roh)
        self.set_location_sensor(current_value, "restart")
        
    def location_changed(self, entity, attribute, old, new, kwargs):
        self.set_location_sensor(new, old)
        
    def process_location(self, location, old_location):
        if location == "Arbeit":
            self.set_state(self.sensor_location_jo, state = "Bei der Arbeit", attributes={"entity_picture":"/local/icons/locations/manager.svg", "friendly_name": self.name_jo})
            time_at_work = self.get_state("sensor.jo_at_work")
            self.log("Time at work: {}".format(time_at_work))
            if time_at_work == "0.0":
                self.fire_event("custom_notify", message="Deiner lieben Frau schreiben!", target="telegram_jo")
        elif location == "home":
            self.set_state(self.sensor_location_jo, state = "Zu Hause", attributes={"entity_picture":"/local/icons/locations/at_home.svg", "friendly_name": self.name_jo})
            if old_location != "home" and old_location != "restart":
                self.log("Jo arrived at home")
                self.fire_event("custom_notify", message="Zu Hause angekommen", target="telegram_jo")
        elif location == "Passat":
            self.set_state(self.sensor_location_jo, state = "Im Auto", attributes={"entity_picture":"/local/icons/locations/car_orange.svg", "friendly_name": self.name_jo})
        elif location == "unterwegs":
            self.set_state(self.sensor_location_jo, state = "Unterwegs", attributes={"entity_picture":"/local/icons/locations/destination.svg", "friendly_name": self.name_jo})
        else:
            self.set_state(self.sensor_location_jo, state = location, attributes={"entity_picture":"/local/icons/weather_warnings/question_mark.svg", "friendly_name": self.name_jo})
