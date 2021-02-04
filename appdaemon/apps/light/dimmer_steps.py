import appdaemon.plugins.hass.hassapi as hass

#
# Helper app, "hearing" for KNX commands and "dim" light in steps
#
# Args:
# - light_entity
# - steps (list of dimming values)
# - command_ga (1 = dim / 0 = off)
#


class dimmer_steps(hass.Hass):

    def initialize(self):
        self.in_action = False
        self.direction = "down"
        self.light = self.args["light_entity"]
        self.steps = self.args["steps"]
        self.timer_handle = None
        # listen for knx events
        self.listen_event(self.received_command, event = "knx_event", destination = self.args["command_ga"])
        
    def received_command(self,event_name,data,kwargs):
        self.log("KNX command for step-dimming detected. Light is: {}. Data is:".format(self.light))
        self.log(data)
        if data["data"] == 0:
            # first, cancel the reset timer
            if self.timer_handle != None:
                self.cancel_timer(self.timer_handle)
            light_state = self.get_state(self.light)
            self.in_action = True
            if light_state == "on":
                self.turn_off(self.light)
                self.log("Switching off {}".format(self.light))
                self.current_brightness = float(0)
                self.direction = "up"
            elif light_state == "off":
                self.turn_on(self.light,brightness=255)
                self.log("Switching on {}".format(self.light))
                self.current_brightness = float(100)
                self.direction = "down"
            else:
                self.log("Light is not on and not off? It is {}".format(light_state))
            self.timer_handle = self.run_in(self.reset, 20)
        elif data["data"] == 1:
            # first, cancel the reset timer
            if self.timer_handle != None:
                self.cancel_timer(self.timer_handle)
            # if first dimming event, check current brightness 
            # (following steps use internal value, as brightness status es sent only after dimming time)
            if not self.in_action:
                try:
                    self.current_brightness = self.byte_to_pct(self.get_state(self.light, attribute="brightness"))
                except:
                    self.current_brightness = float(0)
            self.log("Current Brightness is {}. Will calculate next dimming step now".format(self.current_brightness))
            # up or down?
            if self.current_brightness <= min(self.steps):
                self.log("dimming up")
                self.direction = "up"
            if self.current_brightness >= max(self.steps):
                self.log("dimming down")
                self.direction = "down"
            # find next dimming step
            if self.direction == "up":
                next_step = self.find_next_higher_value()
            else:
                next_step = self.find_next_lower_value()
            self.turn_on(self.light,brightness=self.pct_to_byte(next_step))
            self.current_brightness = next_step
            self.in_action = True
            self.timer_handle = self.run_in(self.reset, 20)
        else:
            self.log("Not 0 and not 1? command_ga should be binary! Please check config")

    def reset(self, kwargs):
        self.in_action = False
        self.direction = "down"
        self.current_brightness = None
        self.timer_handle = None
    
    def find_next_higher_value(self):
        for step in sorted(self.steps):
            higher_value = step
            if step > self.current_brightness:
                break
        return higher_value

    def find_next_lower_value(self):
        for step in sorted(self.steps, reverse=True):
            lower_value = step
            if step < self.current_brightness:
                break
        return lower_value

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
