import appdaemon.plugins.hass.hassapi as hass
import math

#
# App to check humidity value of a sensor and calculate if air from outside can help
#
# Args: see initialize()
# 

class humidity_manager(hass.Hass):

    def initialize(self):
        # Args
        self.sensor_humidity_inside = self.args["sensor_humidity_inside"]
        self.sensor_temp_inside = self.args["sensor_temp_inside"]
        self.sensor_humidity_outside = self.args["sensor_humidity_outside"]
        self.sensor_temp_outside = self.args["sensor_temp_outside"]
        self.max_humidity_inside = self.args["max_humidity_inside"]
        # notification
        self.notification_entity = self.args["notification_entity"]
        self.notification_friendly_name = self.args["notification_friendly_name"]

        self.run_in(self.initialize_delayed,6)
    
    def initialize_delayed(self, kwargs):
        self.attributes_notification_entity = {"icon": "mdi:water-percent", "friendly_name": self.notification_friendly_name}
        
        self.listen_state(self.update_notification, self.sensor_humidity_inside)
        self.listen_state(self.update_notification, self.sensor_temp_inside)
        self.listen_state(self.update_notification, self.sensor_humidity_outside)
        self.listen_state(self.update_notification, self.sensor_temp_outside)
        
        self.update_notification(None, None, None, None, None)

    def update_notification(self, entity, attributes, old, new, kwargs):
        try:
            humidity_inside = float(self.get_state(self.sensor_humidity_inside))
            self.log("Luftfeuchtigkeit innen: {} C".format(round(humidity_inside,1)))
            temp_inside = float(self.get_state(self.sensor_temp_inside))
            self.log("Temperatur innen: {} C".format(round(temp_inside,1)))
            humidity_outside = float(self.get_state(self.sensor_humidity_outside))
            self.log("Luftfeuchtigkeit aussen: {} C".format(round(humidity_outside,1)))
            temp_outside = float(self.get_state(self.sensor_temp_outside))
            self.log("Temperatur aussen: {} C".format(round(temp_outside,1)))
        except:
            self.log("Error converting to float")
        
        if (temp_outside >= 0.0):   # T >= 0 °C
            a_out = 7.5
            b_out = 237.3
        else: # T < 0 °C über Wasser
            a_out = 7.6
            b_out = 240.7

        a_in = 7.5
        b_in = 237.3
        
        SDD_T_out = 6.1078 * math.pow(10.0, (a_out*temp_outside)/(b_out+temp_outside))
        DD_out = humidity_outside/100*SDD_T_out
        v_out = math.log10(DD_out/6.107)
        TD_out = (b_out*v_out)/(a_out-v_out)
        self.log("Taupunkt aussen: {} C".format(round(TD_out,1)))
        SDD_TD_out = 6.1078 * math.pow(10.0, (a_out*TD_out)/(b_out+TD_out))
        SDD_T_in = 6.1078 * math.pow(10.0, (a_in*temp_inside)/(b_in+temp_inside))
        r_in = 100*SDD_TD_out/SDD_T_in
        if r_in > 100.0:
            r_in = 100.0
        self.log("Luftfeuchtigkeit nach Lueften waere {} %".format(round(r_in,1)))
        
        if humidity_inside > self.max_humidity_inside:
            if (r_in < (humidity_inside - 3)) and (r_in < self.max_humidity_inside):
                status = "Bitte lüften! {} => {}%".format(int(round(humidity_inside,0)), int(round(r_in,0)))
            else:
                status = "Luftentfeuchter! Ist {}%".format(int(round(humidity_inside,0)))
        else:
            if r_in < (humidity_inside - 3):
                status = "Lüften möglich ({} => {}%)".format(int(round(humidity_inside,0)), int(round(r_in,0)))
            else:
                status = "Nicht lüften (sonst {} => {}%)".format(int(round(humidity_inside,0)), int(round(r_in,0)))
                
        self.set_state(self.notification_entity, state = status, attributes = self.attributes_notification_entity)
