import appdaemon.plugins.hass.hassapi as hass
from typing import Set
import datetime

#
# Automate light, universal app
#
# Args: 
# - light (light entity that should be controlled)
# - triggers (list of triggers)
# - brightness_values (dict of time and brightness value pairs, for "basic" brightness depending on time. "00:00": XY should be the first)
# - min_illuminance_values (dict of time and illuminance value pairs, for taget illuminance depending on time. "00:00": XY should be the first)
# - illuminance_sensor
# - keeping_off_entities (list of entities, optional)
# - keeping_on_entities (list of entities, optional)
# - keeping_fix_entities (dict of entities:value pairs, optional)
# 

class auto_light_3(hass.Hass):

    def initialize(self):
        self.light: str = self.args.get("light")
        self.triggers: Set[str] = self.args.get("triggers", set())
        # is triggered at the moment of startup?
        self.check_if_any_trigger_active(None)
        # manual mode not implemented yet, so set to false:
        self.manual_mode = False
        self.illuminance_sensor: str = self.args.get("illuminance_sensor", None)
        self.keeping_off_entities: Set[str] = self.args.get("keeping_off_entities", set())
        self.check_if_keeping_off_active(None)
        self.keeping_on_entities: Set[str] = self.args.get("keeping_on_entities", set())
        self.check_if_keeping_on_active(None)
        self.keeping_fix_entities: Set[str] = self.args.get("keeping_fix_entities", set())
        self.log(self.keeping_fix_entities)
        self.check_if_keeping_fix_active(None)
        # brightness depending on time
        self.times_brightness_strings = self.args["brightness_values"].keys()
        self.update_basic_brightness_value(None)
        for each in sorted(self.times_brightness_strings):
            self.run_daily(self.update_basic_brightness_value, datetime.time(int(each.split(":")[0]), int(each.split(":")[1]), 0))
        # min illuminance depending on time
        self.times_min_illuminance_strings = self.args["min_illuminance_values"].keys()
        for each in sorted(self.times_min_illuminance_strings):
            self.run_daily(self.update_min_illuminance_value, datetime.time(int(each.split(":")[0]), int(each.split(":")[1]), 0))
        # measured illuminance
        self.measured_illuminance = float(0)
        if not self.illuminance_sensor == None:
            # set up state listener for illuminance sensor
            self.listen_state(self.illuminance_changed, self.illuminance_sensor)
            try: 
                self.measured_illuminance = float(self.get_state(self.illuminance_sensor))
            except ValueError:
                self.log("illuminance value of sensor {} can not be coverted to float as it is {}".format(self.illuminance_sensor,self.get_state(self.illuminance_sensor)))
        # update min illuminance and check if it is too dark at the moment
        self.update_min_illuminance_value(None)
        # set up state listener for each trigger sensor
        for trigger in self.triggers:
            self.listen_state(self.trigger_state_changed, trigger)
        # set up state listener for each keeping-off entity
        for keeping_off_entity in self.keeping_off_entities:
            self.listen_state(self.keeping_off_entity_changed, keeping_off_entity)
        # set up state listener for each keeping-on entity
        for keeping_on_entity in self.keeping_on_entities:
            self.listen_state(self.keeping_on_entity_changed, keeping_on_entity)
        # set up state listener for each keeping-fix entity
        for keeping_fix_entity in self.keeping_fix_entities:
            self.listen_state(self.keeping_fix_entity_changed, keeping_fix_entity)


    def update_basic_brightness_value(self, kwargs):
        now = datetime.datetime.now()
        for each in sorted(self.times_brightness_strings):
            if now >= now.replace(hour=int(each.split(":")[0]), minute=int(each.split(":")[1])):
                current_brightness = self.args["brightness_values"][each]
        self.basic_brightness = current_brightness
        self.log("Basic brightness set to {}".format(self.basic_brightness))

    def update_min_illuminance_value(self, kwargs):
        now = datetime.datetime.now()
        for each in sorted(self.times_min_illuminance_strings):
            if now >= now.replace(hour=int(each.split(":")[0]), minute=int(each.split(":")[1])):
                current_min_illuminance = self.args["min_illuminance_values"][each]
        self.min_illuminance = current_min_illuminance
        self.log("Min illuminance set to {}".format(self.min_illuminance))
        self.check_if_too_dark(None)

    def illuminance_changed(self, entity, attributes, old, new, kwargs):
        #self.log("illuminance sensor: {} changed from {} to {}".format(entity, old, new))
        try:
            self.measured_illuminance = float(new)
        except Exception as e:
                self.log("Received illuminance can not be coverted to float. will use 0. Error was {}".format(e))
                self.measured_illuminance = float(0)
        self.check_if_too_dark(None)

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

    def filter_turn_on_command(self, kwargs):
        self.log("Will decide now if light should be turned on")
        if self.manual_mode:
            self.log("I am in manual mode, wont do anything")
            return
        if self.keeping_off:
            self.log("A keeping-off entity is active, wont do anything")
            return
        if self.keeping_fix:
            self.log("A keeping-fix entity is active, wont do anything")
            return
        self.log("Will turn on the light now with brightness {}".format(self.basic_brightness))
        self.turn_on(self.light,brightness=self.pct_to_byte(self.basic_brightness))

    def filter_turn_off_command(self, kwargs):
        self.log("Will decide now if light should be turned off")
        if self.manual_mode:
            self.log("I am in manual mode, wont do anything")
            return
        if self.keeping_on:
            self.log("A keeping-on entity is active, wont do anything")
            return
        if self.keeping_fix:
            self.log("A keeping-fix entity is active, wont do anything")
            return
        self.log("Will turn off the light now")
        self.turn_off(self.light)

    def check_if_too_dark(self, kwargs):
        if self.measured_illuminance < self.min_illuminance:
            self.is_too_dark = True
            self.log("is too dark. measured: {}, min_illum.: {}".format(self.measured_illuminance, self.min_illuminance))
        else:
            self.is_too_dark = False
            self.log("is not too dark. measured: {}, min_illum.: {}".format(self.measured_illuminance, self.min_illuminance))

    def check_if_any_trigger_active(self, kwargs):
        self.log("Will check if one of the triggers is active")
        self.is_triggered = False
        for trigger in self.triggers:
            if self.get_state(trigger) == "on":
                self.is_triggered = True

    def keeping_off_entity_changed(self, entity, attributes, old, new, kwargs):
        self.log("Keeping off: {} changed from {} to {}".format(entity, old, new))
        self.check_if_keeping_off_active(None)

    def check_if_keeping_off_active(self, kwargs):
        self.log("Will check if one of the keeping-off devices is active")
        self.keeping_off = False
        self.log("I assume - no.")
        for keeping_off_entity in self.keeping_off_entities:
            if self.get_state(keeping_off_entity) == "on":
                self.keeping_off = True
                self.log("Ah, wait! Yes, this one is active: {}".format(keeping_off_entity))

    def keeping_on_entity_changed(self, entity, attributes, old, new, kwargs):
        self.log("Keeping on: {} changed from {} to {}".format(entity, old, new))
        self.check_if_keeping_on_active(None)

    def check_if_keeping_on_active(self, kwargs):
        self.log("Will check if one of the keeping-on devices is active")
        self.keeping_on = False
        self.log("I assume - no.")
        for keeping_on_entity in self.keeping_on_entities:
            if self.get_state(keeping_on_entity) == "on":
                self.keeping_on = True
                self.log("Ah, wait! Yes, this one is active: {}".format(keeping_on_entity))

    def keeping_fix_entity_changed(self, entity, attributes, old, new, kwargs):
        self.log("Keeping fix: {} changed from {} to {}".format(entity, old, new))
        if new == "on":
            self.keeping_fix = True
            brightness = self.keeping_fix_entities[entity]
            self.log("Will set fixed brightness to {}".format(brightness))
            self.turn_on(self.light,brightness=self.pct_to_byte(brightness))
        else: # this one is not on, but maybe another one
            self.check_if_keeping_fix_active(None)

    def check_if_keeping_fix_active(self, kwargs):
        self.log("Will check if a keeping-fix entity is active. First, I assume - no.")
        self.keeping_fix = False
        for keeping_fix_entity in self.keeping_fix_entities:
            if self.get_state(keeping_fix_entity) == "on":
                self.keeping_fix = True
                self.log("Ah, wait! Yes, this one is active: {}. Will stay in fixed mode".format(keeping_fix_entity))
        if (not self.is_triggered) and (not self.keeping_fix):
            self.filter_turn_off_command(None)

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
    
