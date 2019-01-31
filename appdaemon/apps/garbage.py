import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle garbage topics
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
        self.sensor_reminder_waste = "sensor.restmuelltonne_erinnerung"
        self.sensor_reminder_organic = "sensor.biotonne_erinnerung"
        self.sensor_reminder_paper = "sensor.papiertonne_erinnerung"
        self.sensor_reminder_plastic = "sensor.raweg_erinnerung"
        # --- reminder ---
        time_check_next_day = datetime.time(17, 00, 0)
        self.run_daily(self.check_next_day, time_check_next_day)
        # --- update text at midnight ---
        time_midnight = datetime.time(0, 00, 30)
        self.run_daily(self.update_all, time_midnight)
        # --- listen for calendar updates
        self.listen_state(self.update_waste, self.calendar_waste, attribute="end_time")
        self.listen_state(self.update_organic, self.calendar_organic, attribute="end_time")
        self.listen_state(self.update_paper, self.calendar_paper, attribute="end_time")
        self.listen_state(self.update_plastic, self.calendar_plastic, attribute="end_time")
        self.listen_state(self.reset_waste_reminder, self.calendar_waste, attribute="end_time")
        self.listen_state(self.reset_organic_reminder, self.calendar_organic, attribute="end_time")
        self.listen_state(self.reset_paper_reminder, self.calendar_paper, attribute="end_time")
        self.listen_state(self.reset_plastic_reminder, self.calendar_plastic, attribute="end_time")
        # --- restarts ---
        self.listen_event(self.startup, "plugin_started")
        self.listen_event(self.startup, "appd_started")
        
    def check_next_day(self, kwargs):
        self.log("Checking if tomorrow is some garbage collection")
        # check waste
        if self.calc_days(self.calendar_waste) == 1:
            self.set_state(self.sensor_reminder_waste, state = "on")
            self.notify("Morgen ist Restmülltonne", name = "telegram_jo")
        # check organic
        if self.calc_days(self.calendar_organic) == 1:
            self.set_state(self.sensor_reminder_organic, state = "on")
            self.notify("Morgen ist Biotonne", name = "telegram_jo")
        # check paper
        if self.calc_days(self.calendar_paper) == 1:
            self.set_state(self.sensor_reminder_paper, state = "on")
            self.notify("Morgen ist Papiertonne", name = "telegram_jo")
        # check plastic
        if self.calc_days(self.calendar_plastic) == 1:
            self.set_state(self.sensor_reminder_plastic, state = "on")
            self.notify("Morgen ist RaWeg", name = "telegram_jo")

    def update_waste(self, kwargs):
        self.log("Updating Waste Display Sensor")
        self.create_text(self.calendar_waste, self.sensor_display_waste)

    def update_organic(self, kwargs):
        self.log("Updating Organic Waste Display Sensor")
        self.create_text(self.calendar_organic, self.sensor_display_organic)

    def update_paper(self, kwargs):
        self.log("Updating Paper Display Sensor")
        self.create_text(self.calendar_paper, self.sensor_display_paper)

    def update_plastic(self, kwargs):
        self.log("Updating Plastic Display Sensor")
        self.create_text(self.calendar_plastic, self.sensor_display_plastic)

    def update_all(self, kwargs):
        self.log("Updating All Waste Display Sensors")
        self.update_waste(None)
        self.update_organic(None)
        self.update_paper(None)
        self.update_plastic(None)

    def reset_waste_reminder(self, kwargs):
        self.log("Reseting waste reminder")
        self.set_state(self.sensor_reminder_waste, state = "off")

    def reset_organic_reminder(self, kwargs):
        self.log("Reseting organic waste reminder")
        self.set_state(self.sensor_reminder_organic, state = "off")

    def reset_paper_reminder(self, kwargs):
        self.log("Reseting paper reminder")
        self.set_state(self.sensor_reminder_paper, state = "off")

    def reset_plastic_reminder(self, kwargs):
        self.log("Reseting plastic reminder")
        self.set_state(self.sensor_reminder_plastic, state = "off")

    def startup(self, event_name, data, kwargs):
        self.log("Garbage: Startup detected. Updating all now")
        self.update_all(None)

    def create_text(self, calendar_name, display_sensor_name):
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        days = self.calc_days(calendar_name)
        if days == 0:
            printtext = "heute"
        elif days == 1:
            printtext = "morgen"
        else:
            printtext = end_time_datetime.strftime('{}, %d.%m. ({} T.)').format(weekdays[end_time_datetime.weekday()], days)
        self.set_state(display_sensor_name, state=printtext)
        self.log(printtext)
        
    def calc_days(self, calendar_name):
        end_time_str = self.get_state(calendar_name, attribute="end_time")
        end_time_datetime = datetime.datetime.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
        days = (end_time_datetime.date() - self.datetime().date()).days
        return days
