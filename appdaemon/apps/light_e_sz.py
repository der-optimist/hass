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
        self.listen_state(self.presence_on, "binary_sensor.PM_E_SZ_Bett", new="on")
        self.listen_state(self.presence_off, "binary_sensor.PM_E_SZ_Bett", new="off")
        # react on illuminance change
        self.listen_state(self.illuminance_changed, "sensor.helligkeit_schlafzimmer_pm")
        # react on sleep-switches
        self.listen_state(self.sleep_switch_on, "switch.jo_schlaft", new="on")
        self.listen_state(self.sleep_switch_on, "switch.ma_schlaft", new="on")
        self.listen_state(self.sleep_switch_on, "switch.jo_schlaft", new="off")
        self.listen_state(self.sleep_switch_on, "switch.ma_schlaft", new="off")
    
    def presence_on(self, entity, attributes, old, new, kwargs):
        self.log("PM SZ Bett: {}".format(new))
        if self.get_state(switch.ma_schlaft) == "on" or self.get_state(switch.jo_schlaft) == "on":
            self.log("Bewegung im SZ, aber Ma oder Jo schlaeft. Werde kein Licht anmachen")
        else:
            self.log("Bewegung im SZ, keiner schlaeft, werde schauen ob es zu dunkel ist")
            if self.get_state("sensor.helligkeit_schlafzimmer_pm") < self.min_illuminance:
                self.turn_on("lights.panels_schlafzimmer", brightness_pct=self.brightness_day)
                self.log("War zu dunkel, habe Licht angemacht")
            else:
                self.log("War hell genug, habe das Licht aus gelassen")

    def presence_off(self, entity, attributes, old, new, kwargs):
        self.log("PM SZ Bett: {}".format(new))
        self.turn_off("lights.panels_schlafzimmer")

    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        self.log("Helligkeit SZ: {}".format(new))
        if new >= self.min_illuminance:
            self.log("Helligkeit geaendert, aber mit {} hell genug".format(new))
            return
        if self.get_state(switch.ma_schlaft) == "on" or self.get_state(switch.jo_schlaft) == "on":
            self.log("Ma oder Jo schlaeft. Werde kein Licht anmachen, egal ob Bewegung oder nicht")
        else:
            self.log("Es ist wohl dunkel, keiner schlaeft, werde schauen ob jemand im Raum ist")
            if self.get_state("binary_sensor.PM_E_SZ_Bett") == "on":
                self.turn_on("lights.panels_schlafzimmer", brightness_pct=self.brightness_day)
                self.log("War zu dunkel, es ist jemand da, keiner schlaeft, habe Licht angemacht")
            else:
                self.log("Es ist zwar dunkel und keiner schlaeft, aber es ist niemand da. Habe das Licht aus gelassen")

    def sleep_switch_on(self, entity, attributes, old, new, kwargs):
        self.log("{} meldet: {}".format(entity, new))
        self.turn_off("lights.panels_schlafzimmer")
        
    def sleep_switch_off(self, entity, attributes, old, new, kwargs):
        self.log("{} meldet: {}".format(entity, new))
        if self.get_state(switch.ma_schlaft) == "on" or self.get_state(switch.jo_schlaft) == "on":
            self.log("Ma oder Jo schlaeft noch. Werde kein Licht anmachen, auch wenn jemand aufgestanden ist")
        else:
            self.log("Werde schauen ob jemand im Raum ist und ob es dunkel ist")
            if self.get_state("binary_sensor.PM_E_SZ_Bett") == "on" and self.get_state("sensor.helligkeit_schlafzimmer_pm") < self.min_illuminance:
                self.turn_on("lights.panels_schlafzimmer", brightness_pct=self.brightness_day)
                self.log("War zu dunkel, es ist jemand da, keiner schlaeft, habe Licht angemacht")
            else:
                self.log("Es ist zwar dunkel und keiner schlaeft, aber es ist niemand da. Habe das Licht aus gelassen")
