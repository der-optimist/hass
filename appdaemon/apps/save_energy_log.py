import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# 

class save_energy_log(hass.Hass):

    def initialize(self):
        # args
        #self.temp_limit_max = self.args["temp_limit_max"]
        # run regularly
        time_first_run = datetime.datetime.strptime("00:04:08","%H:%M:%S")
        self.run_every(self.save_log, time_first_run, 30)

    def save_log(self, kwargs):
        pass
