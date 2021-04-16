import appdaemon.plugins.hass.hassapi as hass
import datetime

# Move water valve once a week


class water_valve(hass.Hass):

    def initialize(self):
        run_time =  datetime.time(3, 35, 3)
        self.run_day = 5 # Dienstag
        self.move_valve(None)
        #self.run_daily(self.move_valve, run_time)
        
        
    def move_valve(self, kwargs):
        if self.date().isoweekday() == self.run_day:
            if self.get_state("binary_sensor.pm_e_ba") == "on":
                self.log("Wasserventil nicht bewegt, jemand ist im Bad EG")
                return
            if self.get_state("binary_sensor.pm_e_wc") == "on":
                self.log("Wasserventil nicht bewegt, jemand ist im WC")
                return
            if self.get_state("binary_sensor.pm_o_ba") == "on":
                self.log("Wasserventil nicht bewegt, jemand ist im Bad OG")
                return
            if self.get_state("binary_sensor.waschmaschine_ist_an") == "on":
                self.log("Wasserventil nicht bewegt, Waschmaschine ist an")
                return
            if float(self.get_state("sensor.el_leistung_spulmaschine")) > 0.1:
                self.log("Wasserventil nicht bewegt, Spülmaschine ist an")
                return
            self.turn_off("switch.wasserabsperrventil")
            self.log("Habe Wasser ausgeschalten")
            self.run_in(self.turn_on_valve,40)

    def turn_on_valve(self, kwargs):
        self.turn_on("switch.wasserabsperrventil")
        self.log("Habe Wasser wieder eingeschalten")
