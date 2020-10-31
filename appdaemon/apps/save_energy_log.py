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
        ts_local = datetime.datetime.now().timestamp()
        power_compare = float(self.get_state("sensor.el_leistung_licht_sicherung_3_3"))
        line = "{}\t{}\t{}\t{}\t{}\t{}".format(ts_local,power,apparentpower,cos_phi,energy,power_compare)
        self.log(line)
        with open("/config/appdaemon/logs/energy_log_licht_3_3.tab", "a") as myfile:
            myfile.write(line)
