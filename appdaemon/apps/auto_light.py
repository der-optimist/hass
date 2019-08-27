import appdaemon.plugins.hass.hassapi as hass
from typing import Set

#
# Automate light, universal app
#
# Args: 
# - light: light entity that shall be automated
# - triggers: list of sensors that trigger the light 
# - blocking_entities: list of entities that block this app (e.g. sleeping-switch)
# - brightness_day
# - brightness_night
# - min_illuminance_day
# - min_illuminance_night
# - illuminance_sensor
# - trigger_entities_for_night_mode: on = night
# 

class auto_light(hass.Hass):

    def initialize(self):
        # args to app-variables
        self.brightness_day = float(self.args.get("brightness_day"))
        self.brightness_night = float(self.args.get("brightness_night"))
        self.min_illuminance_day = float(self.args.get("min_illuminance_day"))
        self.min_illuminance_night = float(self.args.get("min_illuminance_night"))
        self.light: str = self.args.get("light")
        self.triggers: Set[str] = self.args.get("triggers", set())
        self.blocking_entities: Set[str] = self.args.get("blocking_entities", set())
        self.illuminance_sensor: str = self.args.get("illuminance_sensor", None)
        self.trigger_entities_for_night_mode: Set[str] = self.args.get("trigger_entities_for_night_mode", set())
        
        # read current status from devices and save in internal variables
        # is_blocked
        self.check_if_blocked(None)
        # manual_mode
        self.manual_mode = False
        # measured_brightness
        self.measured_illuminance = float(0)
        if not self.illuminance_sensor == None:
            try: 
                self.measured_illuminance = float(self.get_state(self.illuminance_sensor))
            except ValueError:
                self.log("illuminance value of sensor {} can not be coverted to float as it is {}".format(self.illuminance_sensor,self.get_state(self.illuminance_sensor)))
        # is_night
        self.check_if_night(None)
        for trigger_entity_for_night_mode in self.trigger_entities_for_night_mode:
            self.listen_state(self.night_trigger_changed, trigger_entity_for_night_mode)
        self.check_if_any_trigger_active(None)
        self.app_brightness_state = float(self.get_state(self.light, attribute="brightness_pct"))
        
        # set up state listener for each trigger sensor
        for trigger in self.triggers:
            self.listen_state(self.trigger_state_changed, trigger)
        # set up state listener for the light
        self.listen_state(self.light_state_changed, self.light, attribute="brightness_pct")
        # set up state listener for brightness sensor
        self.listen_state(self.illuminance_changed, self.illuminance_sensor)
        # set up state listener for each blocking entity
        for blocking_entity in self.blocking_entities:
            self.listen_state(self.blocking_entity_changed, blocking_entity)
        
    def trigger_state_changed(self, entity, attributes, old, new, kwargs):
        self.log("Light Trigger: {} changed from {} to {}".format(entity, old, new))
        if new == "on":
            if self.is_triggered:
                self.log("Got trigger event, but is already triggered, wont do anything")
                return
            else:
                self.is_triggered = True
                self.log("Got trigger event ON, will check if it is too dark...")
                if self.is_too_dark:
                    self.log("Jep, seems to be too dark")
                    self.filter_turn_on_command(None)
        if new == "off":
            self.log("Got trigger event OFF, will look if another trigger is active")
            self.check_if_any_trigger_active(None)
            if self.is_triggered:
                self.log("Another trigger is active. Will do nothing with this OFF event")
            else:
                self.log("No other trigger is active, noboby seems to be here. Will decide if I should switch the light off")
                self.log("But first, I will activate automatic mode")
                self.manual_mode = False
                self.filter_turn_off_command(None)
        
    def light_state_changed(self, entity, attributes, old, new, kwargs):
        self.log("Light: {} changed from {} to {}".format(entity, old, new))
        if float(new) == self.app_brightness_state:
            # does this work for OFF? No brightness?
            self.log("This state change happened most likely due to my command. Wont change anything")
        else:
            self.log("The light was changed manually, I think. Will deactivate myself and switch to manual mode")
            self.manual_mode = True
        
    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        self.log("illuminance sensor: {} changed from {} to {}".format(entity, old, new))
        self.measured_illuminance = float(new)
        self.check_if_too_dark(None)
        if self.is_too_dark and self.is_triggered:
            self.log("Seems to be too dark and someone is present. Will decide if I should switch on the light")
            self.filter_turn_on_command(None)
        
    def blocking_entity_changed(self, entity, attributes, old, new, kwargs):
        self.log("Blocking: {} changed from {} to {}".format(entity, old, new))
        self.check_if_blocked(None)
    
    def night_trigger_changed(self, entity, attributes, old, new, kwargs):
        self.log("Night trigger: {} changed from {} to {}".format(entity, old, new))
        self.check_if_night(None)
        self.check_if_too_dark(None)
        if self.is_too_dark and self.is_triggered:
            self.log("Seems to be too dark and someone is present. Will decide if I should switch on the light")
            self.filter_turn_on_command(None)

    def filter_turn_on_command(self, kwargs):
        self.log("Will decide now if light should be turned on")
        if self.manual_mode:
            self.log("I am in manual mode, wont do anything")
            return
        if self.is_blocked:
            self.log("I am blocked by a blocking entity, wont do anything")
            return
        self.log("Will turn on the light now")
        if self.is_night:
            self.app_brightness_state = self.brightness_night
            self.turn_on(self.light,brightness=self.brightness_night)
        else:
            self.app_brightness_state = self.brightness_day
            self.turn_on(self.light,brightness=self.brightness_day)
    
    def filter_turn_off_command(self, kwargs):
        self.log("Will decide now if light should be turned off")
        if self.manual_mode:
            self.log("I am in manual mode, wont do anything")
            return
        if self.is_blocked:
            self.log("I am blocked by a blocking entity, wont do anything")
            return
        self.log("Will turn off the light now")
        self.app_brightness_state = float(0)
        self.turn_off(self.light)
        
    def check_if_blocked(self, kwargs):
        self.log("Will check if one of the blocking device is active")
        self.is_blocked = False
        for blocking_entity in self.blocking_entities:
            if self.get_state(blocking_entity) == "on":
                self.is_blocked = True
    
    def check_if_any_trigger_active(self, kwargs):
        self.log("Will check if one of the triggers is active")
        self.is_triggered = False
        for trigger in self.triggers:
            if self.get_state(trigger) == "on":
                self.is_triggered = True
    
    def check_if_too_dark(self, kwargs):
        if self.is_night:
            if self.measured_illuminance < self.min_illuminance_night:
                self.is_too_dark = True
            else:
                self.is_too_dark = False
        else:
            if self.measured_illuminance < self.min_illuminance_day:
                self.is_too_dark = True
            else:
                self.is_too_dark = False
                
    def check_if_night(self, kwargs):
        self.is_night = False
        for trigger_entity_for_night_mode in self.trigger_entities_for_night_mode:
            if self.get_state(trigger_entity_for_night_mode) == "on":
                self.is_night = True
