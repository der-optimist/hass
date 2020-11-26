import appdaemon.plugins.hass.hassapi as hass

#
# App to turn lights on/off outside with an aqara cube
#
# Args: see initialize()
# 

class cube_terrasse(hass.Hass):

    def initialize(self):
        # Args
        self.zha_device_ieee = self.args["zha_device_ieee"]
        
        self.active_side = None
        #self.listen_event(self.cube_flip, "zha_event", device_ieee = self.zha_device_ieee, command = "flip")
        self.listen_event(self.cube_shake, "zha_event", device_ieee = self.zha_device_ieee, command = "shake")
        #self.listen_event(self.cube_knock, "zha_event", device_ieee = self.zha_device_ieee, command = "knock")
        #self.listen_event(self.cube_rotate_right, "zha_event", device_ieee = self.zha_device_ieee, command = "rotate_right")
        #self.listen_event(self.cube_rotate_left, "zha_event", device_ieee = self.zha_device_ieee, command = "rotate_left")
        
        
    def cube_flip(self,event_name,data,kwargs):
        self.active_side = data["args"]["activated_face"]
        self.log("Active Side: {}".format(self.active_side))
    
    def cube_shake(self,event_name,data,kwargs):
#        if self.get_state("light.wandwurfel_suden") == "on":
#            wandwurfel_suden = True
#        else:
#            wandwurfel_suden = False
#        if self.get_state("light.wandwurfel_westen") == "on":
#            wandwurfel_westen = True
#        else:
#            wandwurfel_westen = False
#            
#        if wandwurfel_suden or wandwurfel_westen:
#            self.turn_off("light.wandwurfel_suden")
#            self.turn_off("light.wandwurfel_westen")
#            self.log("Beide oder ein Wandwürfel waren an, habe sie aus gemacht")
#        else:
#            self.turn_on("light.wandwurfel_suden")
#            self.turn_on("light.wandwurfel_westen")
#            self.log("Beide Wandwürfel waren aus, habe sie an gemacht")

        if self.get_state("light.panels_wc") == "on":
            self.turn_off("light.panels_wc")
            self.turn_off("light.spiegel_wc")
            #self.turn_off("input_boolean.app_switch_licht_wc")
        else:
            #self.turn_on("input_boolean.app_switch_licht_wc")
            self.turn_on("light.panels_wc",brightness=178)
            self.turn_on("light.spiegel_wc")


    def cube_knock(self,event_name,data,kwargs):
        self.active_side = data["args"]["activated_face"]
        self.log("Active Side: {}".format(self.active_side))
        if self.active_side == 5:
            self.toggle("light.wandwurfel_suden")
            self.log("toggled Würfel Süd")
        elif self.active_side == 1:
            self.toggle("light.wandwurfel_westen")
            self.log("toggled Würfel Westen")
    
    def cube_rotate_right(self,event_name,data,kwargs):
        if self.active_side == 5:
            self.turn_on("light.wandwurfel_suden")
            self.log("Würfel Süd an gemach wegen Rotate Right")
        elif self.active_side == 1:
            self.turn_on("light.wandwurfel_westen")
            self.log("Würfel Westen an gemach wegen Rotate Right")
        else:
            self.log("Rotate Right erkannt, aber active side ist {}".format(self.active_side))
    
    def cube_rotate_left(self,event_name,data,kwargs):
        if self.active_side == 5:
            self.turn_off("light.wandwurfel_suden")
            self.log("Würfel Süd aus gemach wegen Rotate Left")
        elif self.active_side == 1:
            self.turn_off("light.wandwurfel_westen")
            self.log("Würfel Westen aus gemach wegen Rotate Left")
        else:
            self.log("Rotate Left erkannt, aber active side ist {}".format(self.active_side))
            
