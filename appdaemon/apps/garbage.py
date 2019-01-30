import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App to handle garbage topics
#
# Args: 
# 

class garbage(hass.Hass):

    def initialize(self):
        time_check_next_day = datetime.time(17, 00, 0)
        self.run_daily(self.check_next_day, time_check_next_day)
        self.listen_state(self.update_waste, "calendar.restmuelltonne", attribute="end_time")
        # for testing:
        self.run_minutely(self.update_waste, time_check_next_day)
        
    def check_next_day(self, entity, attribute, old, new, kwargs):
        pass

    def update_waste(self, kwargs):
        end_time_str = self.get_state("calendar.restmuelltonne", attribute="end_time")
        end_time_datetime = datetime.datetime.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
        self.log(end_time_datetime)
        self.log(type(end_time_datetime))
        display_text = self.create_text(end_time_datetime)
        self.set_state("sensor.restmuell_anzeige", state=display_text)

    def update_organic(self, entity, attribute, old, new, kwargs):
        pass

    def update_paper(self, entity, attribute, old, new, kwargs):
        pass

    def update_plastic(self, entity, attribute, old, new, kwargs):
        pass

    def update_all(self, entity, attribute, old, new, kwargs):
        pass

    def create_text(self, start_date):
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        days = (start_date.date() - self.datetime().date()).days
        if days == 0:
            printtext = "heute"
        elif days == 1:
            printtext = "morgen"
        else:
            printtext = start_date.strftime('{}, %d.%m. ({} T.)').format(weekdays[start_date.weekday()], days)
        return printtext
