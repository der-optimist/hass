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
#        self.run_every(self.save_log, time_first_run, 30)                      #!!! disabled

    def save_log(self, kwargs):
        # POW R2 1 - Licht 3.3
        #power = float(self.get_state("sensor.sonoff_pow_r2_1_wirkleistung"))
        #apparentpower = float(self.get_state("sensor.sonoff_pow_r2_1_scheinleistung"))
        #cos_phi = float(self.get_state("sensor.sonoff_pow_r2_1_leistungsfaktor"))
        #energy = float(self.get_state("sensor.sonoff_pow_r2_1_energie"))
        #ts_local = datetime.datetime.now().timestamp()
        #power_compare = float(self.get_state("sensor.el_leistung_licht_sicherung_3_3"))
        #line = "\n{}\t{}\t{}\t{}\t{}\t{}".format(ts_local,power,apparentpower,cos_phi,energy,power_compare)
        #self.log(line)
        #with open("/config/appdaemon/logs/energy_log_licht_3_3_v2.tab", "a") as myfile:
        #    myfile.write(line)

        # POW R2 2 - Kühlschrank Küche
        power = float(self.get_state("sensor.sonoff_pow_r2_2_wirkleistung"))
        apparentpower = float(self.get_state("sensor.sonoff_pow_r2_2_scheinleistung"))
        cos_phi = float(self.get_state("sensor.sonoff_pow_r2_2_leistungsfaktor"))
        energy = float(self.get_state("sensor.sonoff_pow_r2_2_energie"))
        ts_local = datetime.datetime.now().timestamp()
        power_compare = float(self.get_state("sensor.el_leistung_kuhlschrank_kuche"))
        line = "\n{}\t{}\t{}\t{}\t{}\t{}".format(ts_local,power,apparentpower,cos_phi,energy,power_compare)
        #self.log(line)
        with open("/config/appdaemon/logs/energy_log_kuehlschrank_kueche.tab", "a") as myfile:
            myfile.write(line)

        # Tasmota SD 2- Spülmaschine
        power = float(self.get_state("sensor.tasmota_sd_2_wirkleistung"))
        apparentpower = float(self.get_state("sensor.tasmota_sd_2_scheinleistung"))
        cos_phi = float(self.get_state("sensor.tasmota_sd_2_leistungsfaktor"))
        energy = float(self.get_state("sensor.tasmota_sd_2_energie"))
        ts_local = datetime.datetime.now().timestamp()
        power_compare = float(self.get_state("sensor.el_leistung_spulmaschine"))
        line = "\n{}\t{}\t{}\t{}\t{}\t{}".format(ts_local,power,apparentpower,cos_phi,energy,power_compare)
        #self.log(line)
        with open("/config/appdaemon/logs/energy_log_spuelmaschine.tab", "a") as myfile:
            myfile.write(line)

        # Tasmota SD 3- Kodi-Platte
        power = float(self.get_state("sensor.tasmota_sd_3_wirkleistung"))
        apparentpower = float(self.get_state("sensor.tasmota_sd_3_scheinleistung"))
        cos_phi = float(self.get_state("sensor.tasmota_sd_3_leistungsfaktor"))
        energy = float(self.get_state("sensor.tasmota_sd_3_energie"))
        ts_local = datetime.datetime.now().timestamp()
        power_compare = 0.0 #float(self.get_state("sensor.el_leistung_lg_anlage"))
        line = "\n{}\t{}\t{}\t{}\t{}\t{}".format(ts_local,power,apparentpower,cos_phi,energy,power_compare)
        #self.log(line)
        with open("/config/appdaemon/logs/energy_log_kodi_platte.tab", "a") as myfile:
            myfile.write(line)
