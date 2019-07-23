import appdaemon.plugins.hass.hassapi as hass

#
# Automate light: SZ
#
# Args: 
# 

class light_e_sz(hass.Hass):

    def initialize(self):
        # set values
        self.brightness_day = 100 # %
        self.min_illuminance = 100 # lx
        # react on presence detection
        self.listen_state(self.presence_on, "binary_sensor.PM_E_SZ_Bett", new="on", old="off")
        self.listen_state(self.presence_off, "binary_sensor.PM_E_SZ_Bett", new="off", old="on")
        # react on illuminance change
        self.listen_state(self.illuminance_changed, "sensor.helligkeit_schlafzimmer_pm")
    
    def presence_on(self, entity, attributes, old, new, kwargs):
        self.log("PM SZ Bett: {}".format(new))
        if self.get_state(switch.ma_schlaft) == "on" or self.get_state(switch.jo_schlaft) == "on":
            self.log("Bewegung im SZ, aber Ma oder Jo schlaeft. Werde kein Licht anmachen")
        else:
            self.log("Bewegung im SZ, keiner schlaeft, werde schauen ob es zu dunkel ist")
            if self.get_state("sensor.helligkeit_schlafzimmer_pm") < self.min_illuminance:
                self_turn_on("lights.panels_schlafzimmer", brightness_pct=self.brightness_day)
                self.log("War zu dunkel, habe Licht angemacht")
            else:
                self.log("War hell genug, habe das Licht aus gelassen")

    def presence_off(self, entity, attributes, old, new, kwargs):
        self.log("PM SZ Bett: {}".format(new))

    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        self.log("Helligkeit SZ: {}".format(new))
