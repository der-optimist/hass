import appdaemon.plugins.hass.hassapi as hass
import datetime

# Move water valve once a week


class water_valve(hass.Hass):

    def initialize(self):
        run_time =  datetime.time(3, 35, 3)
        self.run_day = 5
        self.move_valve(None)
        #self.run_daily(self.move_valve, run_time)
        
        
    def move_valve(self, kwargs):
        self.log(self.date().isoweekday())
        if self.date().isoweekday() == self.run_day:
            self.log("jo")
