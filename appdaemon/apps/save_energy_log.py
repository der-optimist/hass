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
        power = float(self.get_state("sensor.sonoff_pow_r2_1_wirkleistung"))
        apparentpower = float(self.get_state("sensor.sonoff_pow_r2_1_scheinleistung"))
        cos_phi = float(self.get_state("sensor.sonoff_pow_r2_1_leistungsfaktor"))
        energy = float(self.get_state("sensor.sonoff_pow_r2_1_energie"))
        ts_local = datetime.datetime.strptime(date_str + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        line = "{}\t{}\t{}\t{}\\t{}".format(ts_local,power,apparentpower,cos_phi,energy)
        with open("/config/appdaemon/logs/energy_log.tab", "a") as myfile:
            myfile.write(line)
