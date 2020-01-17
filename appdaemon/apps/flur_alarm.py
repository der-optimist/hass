import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when things happen:
#  - motion
#
# Args:
#

class flur_alarm(hass.Hass):

    def initialize(self):
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_o_fl_treppe")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_e_fl_treppe_og")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_e_fl_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_e_wf_flur")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_e_wf_garderobe")
        self.listen_state(self.sensor_state_changed, "binary_sensor.pm_e_wf_haustur")
        self.target = self.args["target"]
    
    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        #self.log(old)
        #self.log(new)
        if new == "on" and old != "on":
            if entity == "binary_sensor.pm_o_fl_flur":
                readable_name = "Flur OG"
            elif entity == "binary_sensor.pm_o_fl_treppe":
                readable_name = "Treppe OG (oben)"
            elif entity == "binary_sensor.pm_e_fl_treppe_og":
                readable_name = "Treppe OG (unten)"
            elif entity == "binary_sensor.pm_e_fl_flur":
                readable_name = "Flur EG"
            elif entity == "binary_sensor.pm_e_wf_flur":
                readable_name = "Flur EG"
            elif entity == "binary_sensor.pm_e_wf_garderobe":
                readable_name = "Windfang Garderobe"
            elif entity == "binary_sensor.pm_e_wf_haustur":
                readable_name = "Windfang Haustür"
            else:
                readable_name = entity.replace("binary_sensor.","").replace("pm_","").replace("_"," ")
            message="Bewegung! => {}".format(readable_name)
            self.fire_event("custom_notify", message=message, target=self.target)
