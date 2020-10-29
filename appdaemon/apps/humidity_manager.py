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

        self.run_in(self.initialize_delayed,86)
    
    def initialize_delayed(self, kwargs):
        icon = "/local/icons/reminders/drop_orange_blink.svg"
        self.attributes_notification_entity = {"entity_picture": icon, "friendly_name": self.notification_friendly_name}
        
        self.listen_state(self.update_notification, self.sensor_humidity_inside)
        self.listen_state(self.update_notification, self.sensor_temp_inside)
        self.listen_state(self.update_notification, self.sensor_humidity_outside)
        self.listen_state(self.update_notification, self.sensor_temp_outside)
        
        self.update_notification(None, None, None, None, None)

    def update_notification(self, entity, attributes, old, new, kwargs):
        try:
            humidity_inside = float(self.get_state(self.sensor_humidity_inside))
            temp_inside = float(self.get_state(self.sensor_temp_inside))
            humidity_outside = float(self.get_state(self.sensor_humidity_outside))
            temp_outside = float(self.get_state(self.sensor_temp_outside))
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
        self.log("Taupunkt aussen: {}°C".format(round(TD_out,1)))
        SDD_TD_out = 6.1078 * math.pow(10.0, (a_out*TD_out)/(b_out+TD_out))
        SDD_T_in = 6.1078 * math.pow(10.0, (a_in*temp_inside)/(b_in+temp_inside))
        r_in = 100*SDD_TD_out/SDD_T_in
        self.log("Luftfeuchtigkeit nach Lueften waere {}%".format(round(r_in,1)))
        
        #self.set_state(self.name_reminder_switch_tank_full, state = "off", attributes = self.attributes_reminder_tank_full)
