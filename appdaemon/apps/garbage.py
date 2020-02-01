import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle garbage topics
# (note: AD-created switched are toggled by separate app)
# 
# Args: no args required 
# 

class garbage(hass.Hass):

    def initialize(self):
        # --- calendar and sensor names ---
        self.calendar_waste = "calendar.restmuelltonne"
        self.calendar_organic = "calendar.biotonne"
        self.calendar_paper = "calendar.papiertonne"
        self.calendar_plastic = "calendar.raweg"
        self.sensor_display_waste = "sensor.restmuelltonne_anzeige"
        self.sensor_display_organic = "sensor.biotonne_anzeige"
        self.sensor_display_paper = "sensor.papiertonne_anzeige"
        self.sensor_display_plastic = "sensor.raweg_anzeige"
        self.sensor_display_1 = "sensor.abfall_anzeige_1"
        self.sensor_display_2 = "sensor.abfall_anzeige_2"
        self.sensor_display_3 = "sensor.abfall_anzeige_3"
        self.sensor_display_4 = "sensor.abfall_anzeige_4"
        self.switch_reminder_waste = "switch.reminder_garbage_restmuelltonne"
        self.switch_reminder_organic = "switch.reminder_garbage_biotonne"
        self.switch_reminder_paper = "switch.reminder_garbage_papiertonne"
        self.switch_reminder_plastic = "switch.reminder_garbage_raweg"
        self.icon_waste = "/local/icons/garbage/tonne_grau.svg"
        self.icon_organic = "/local/icons/garbage/tonne_braun.svg"
        self.icon_paper = "/local/icons/garbage/tonne_blau.svg"
        self.icon_plastic = "/local/icons/garbage/tonne_gelb.svg"
        self.icon_waste_blink = "/local/icons/garbage/tonne_grau_blink.svg"
        self.icon_organic_blink = "/local/icons/garbage/tonne_braun_blink.svg"
        self.icon_paper_blink = "/local/icons/garbage/tonne_blau_blink.svg"
        self.icon_plastic_blink = "/local/icons/garbage/tonne_gelb_blink.svg"
        # --- reminder ---
        time_check_next_day = datetime.time(17, 00, 0)
        self.run_daily(self.check_next_day, time_check_next_day)
        # --- update text at midnight ---
        time_midnight = datetime.time(0, 00, 30)
        self.run_daily(self.midnight, time_midnight)
        # --- listen for calendar updates
        self.listen_state(self.end_waste, self.calendar_waste, attribute="end_time")
        self.listen_state(self.end_organic, self.calendar_organic, attribute="end_time")
        self.listen_state(self.end_paper, self.calendar_paper, attribute="end_time")
        self.listen_state(self.end_plastic, self.calendar_plastic, attribute="end_time")
        # --- restarts ---
        #self.listen_event(self.startup, "plugin_started")
        #self.listen_event(self.startup, "appd_started")
        # --- initialize sensors and switches
        self.create_display_sensors(None)
        self.create_reminder_switches(None)
        self.run_in(self.update_all_displays, 30)
        
    def check_next_day(self, kwargs):
        self.log("Checking if tomorrow is some garbage collection")
        # check waste
        if self.calc_days(self.calendar_waste) == 1:
            self.log("Tomorrow is waste collection")
            self.set_state(self.switch_reminder_waste, state = "on")
            self.fire_event("custom_notify", message="Morgen ist Restmülltonne", target="telegram_jo")
        # check organic
        if self.calc_days(self.calendar_organic) == 1:
            self.log("Tomorrow is organic waste collection")
            self.set_state(self.switch_reminder_organic, state = "on")
            self.fire_event("custom_notify", message="Morgen ist Biotonne", target="telegram_jo")
        # check paper
        if self.calc_days(self.calendar_paper) == 1:
            self.log("Tomorrow is paper collection")
            self.set_state(self.switch_reminder_paper, state = "on")
            self.fire_event("custom_notify", message="Morgen ist Papiertonne", target="telegram_jo")
        # check plastic
        if self.calc_days(self.calendar_plastic) == 1:
            self.log("Tomorrow is plastic collection")
            self.set_state(self.switch_reminder_plastic, state = "on")
            self.fire_event("custom_notify", message="Morgen ist RaWeg", target="telegram_jo")

    def end_waste(self, entity, attribute, old, new, kwargs):
        if new is not None:
            self.update_waste_display(None)
        self.log("Reseting waste reminder")
        self.set_state(self.switch_reminder_waste, state = "off")

    def end_organic(self, entity, attribute, old, new, kwargs):
        if new is not None:
            self.update_organic_display(None)
        self.log("Reseting organic waste reminder")
        self.set_state(self.switch_reminder_organic, state = "off")

    def end_paper(self, entity, attribute, old, new, kwargs):
        if new is not None:
            self.update_paper_display(None)
        self.log("Reseting paper reminder")
        self.set_state(self.switch_reminder_paper, state = "off")

    def end_plastic(self, entity, attribute, old, new, kwargs):
        if new is not None:
            self.update_plastic_display(None)
        self.log("Reseting plastic reminder")
        self.set_state(self.switch_reminder_plastic, state = "off")
    
    def update_waste_display(self, kwargs):
        self.log("Updating Waste Display Sensor")
        self.create_text(self.calendar_waste, self.sensor_display_waste)
        self.update_sorted_sensors(None)

    def update_organic_display(self, kwargs):
        self.log("Updating Organic Waste Display Sensor")
        self.create_text(self.calendar_organic, self.sensor_display_organic)
        self.update_sorted_sensors(None)

    def update_paper_display(self, kwargs):
        self.log("Updating Paper Display Sensor")
        self.create_text(self.calendar_paper, self.sensor_display_paper)
        self.update_sorted_sensors(None)

    def update_plastic_display(self, kwargs):
        self.log("Updating Plastic Display Sensor")
        self.create_text(self.calendar_plastic, self.sensor_display_plastic)
        self.update_sorted_sensors(None)

    def midnight(self, kwargs):
        self.log("Midnight - Updating All Waste Display Sensors")
        self.update_all_displays(None)

    def startup(self, event_name, data, kwargs):
        self.log("Garbage: Startup detected. Updating all the stuff now")
        self.create_display_sensors(None)
        self.create_reminder_switches(None)
        self.update_all_displays(None)

    def update_all_displays(self, kwargs):
        self.update_waste_display(None)
        self.update_organic_display(None)
        self.update_paper_display(None)
        self.update_plastic_display(None)

    def create_reminder_switches(self, kwargs):
        if self.entity_exists(self.switch_reminder_waste):
            curr_state = self.get_state(self.switch_reminder_waste)
            self.set_state(self.switch_reminder_waste, state = curr_state, attributes={"entity_picture":self.icon_waste_blink, "friendly_name": "Restmülltonne raus"})
        else:
            self.set_state(self.switch_reminder_waste, state = "off", attributes={"entity_picture":self.icon_waste_blink, "friendly_name": "Restmülltonne raus"})
        if self.entity_exists(self.switch_reminder_organic):
            curr_state = self.get_state(self.switch_reminder_organic)
            self.set_state(self.switch_reminder_organic, state = curr_state, attributes={"entity_picture":self.icon_organic_blink, "friendly_name": "Biotonne raus"})
        else:
            self.set_state(self.switch_reminder_organic, state = "off", attributes={"entity_picture":self.icon_organic_blink, "friendly_name": "Biotonne raus"})
        if self.entity_exists(self.switch_reminder_paper):
            curr_state = self.get_state(self.switch_reminder_paper)
            self.set_state(self.switch_reminder_paper, state = curr_state, attributes={"entity_picture":self.icon_paper_blink, "friendly_name": "Papiertonne raus"})
        else:
            self.set_state(self.switch_reminder_paper, state = "off", attributes={"entity_picture":self.icon_paper_blink, "friendly_name": "Papiertonne raus"})
        if self.entity_exists(self.switch_reminder_plastic):
            curr_state = self.get_state(self.switch_reminder_plastic)
            self.set_state(self.switch_reminder_plastic, state = curr_state, attributes={"entity_picture":self.icon_plastic_blink, "friendly_name": "RaWeg herrichten"})
        else:
            self.set_state(self.switch_reminder_plastic, state = "off", attributes={"entity_picture":self.icon_plastic_blink, "friendly_name": "RaWeg herrichten"})

    def create_display_sensors(self, kwargs):
        if self.entity_exists(self.sensor_display_waste):
            curr_state = self.get_state(self.sensor_display_waste)
            self.set_state(self.sensor_display_waste, state = curr_state, attributes={"entity_picture":self.icon_waste, "friendly_name": "Restmüll"})
        else:
            self.set_state(self.sensor_display_waste, state = "warte...", attributes={"entity_picture":self.icon_waste, "friendly_name": "Restmüll", "timestamp": 0})
        if self.entity_exists(self.sensor_display_organic):
            curr_state = self.get_state(self.sensor_display_organic)
            self.set_state(self.sensor_display_organic, state = curr_state, attributes={"entity_picture":self.icon_organic, "friendly_name": "Biotonne"})
        else:
            self.set_state(self.sensor_display_organic, state = "warte...", attributes={"entity_picture":self.icon_organic, "friendly_name": "Biotonne", "timestamp": 0})
        if self.entity_exists(self.sensor_display_paper):
            curr_state = self.get_state(self.sensor_display_paper)
            self.set_state(self.sensor_display_paper, state = curr_state, attributes={"entity_picture":self.icon_paper, "friendly_name": "Papiertonne"})
        else:
            self.set_state(self.sensor_display_paper, state = "warte...", attributes={"entity_picture":self.icon_paper, "friendly_name": "Papiertonne", "timestamp": 0})
        if self.entity_exists(self.sensor_display_plastic):
            curr_state = self.get_state(self.sensor_display_plastic)
            self.set_state(self.sensor_display_plastic, state = curr_state, attributes={"entity_picture":self.icon_plastic, "friendly_name": "RaWeg"})
        else:
            self.set_state(self.sensor_display_plastic, state = "warte...", attributes={"entity_picture":self.icon_plastic, "friendly_name": "RaWeg", "timestamp": 0})
        self.set_state(self.sensor_display_1, state = "warte...")
        self.set_state(self.sensor_display_2, state = "warte...")
        self.set_state(self.sensor_display_3, state = "warte...")
        self.set_state(self.sensor_display_4, state = "warte...")

    def create_text(self, calendar_name, display_sensor_name):
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        days = self.calc_days(calendar_name)
        end_time_datetime = self.get_end_time(calendar_name)
        if days == 0:
            printtext = "heute"
        elif days == 1:
            printtext = "morgen"
        else:
            printtext = end_time_datetime.strftime('{}, %d.%m. ({} T.)').format(weekdays[end_time_datetime.weekday()], days)
        self.set_state(display_sensor_name, state=printtext, attributes={"timestamp":end_time_datetime.timestamp()})
        #self.log(printtext)
        
    def calc_days(self, calendar_name):
        end_time_datetime = self.get_end_time(calendar_name)
        days = (end_time_datetime.date() - self.datetime().date()).days
        return days

    def get_end_time(self, calendar_name):
        end_time_str = self.get_state(calendar_name, attribute="end_time")
        end_time_datetime = datetime.datetime.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
        return end_time_datetime

    def update_sorted_sensors(self, kwargs):
        sensor_names = [self.sensor_display_waste, self.sensor_display_organic, self.sensor_display_paper, self.sensor_display_plastic]
        timestamps = []
        for sensor in sensor_names:
            timestamps.append(self.get_state(sensor, attribute = "timestamp"))
        self.log(timestamps)
        zipped_pairs = zip(timestamps, sensor_names)
        sensor_names_sorted = [x for _, x in sorted(zipped_pairs)] 
        self.set_state(self.sensor_display_1, state = self.get_state(sensor_names_sorted[0]), attributes={"entity_picture":self.get_state(sensor_names_sorted[0], attribute = "entity_picture"), "friendly_name":self.get_state(sensor_names_sorted[0], attribute = "friendly_name")})
        self.set_state(self.sensor_display_2, state = self.get_state(sensor_names_sorted[1]), attributes={"entity_picture":self.get_state(sensor_names_sorted[1], attribute = "entity_picture"), "friendly_name":self.get_state(sensor_names_sorted[1], attribute = "friendly_name")})
        self.set_state(self.sensor_display_3, state = self.get_state(sensor_names_sorted[2]), attributes={"entity_picture":self.get_state(sensor_names_sorted[2], attribute = "entity_picture"), "friendly_name":self.get_state(sensor_names_sorted[2], attribute = "friendly_name")})
        self.set_state(self.sensor_display_4, state = self.get_state(sensor_names_sorted[3]), attributes={"entity_picture":self.get_state(sensor_names_sorted[3], attribute = "entity_picture"), "friendly_name":self.get_state(sensor_names_sorted[3], attribute = "friendly_name")})
        
        
