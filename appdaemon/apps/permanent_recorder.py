import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient

# Saves a state or an attribute to an influx db (like recorder, but less data => permanent)
#
# Args:
# - light_brightness (list of light entities, brightness is saved. on/off lights = 100%/0%)
# - state_string (list of entities, state is saved)
# - state_binary (list of entities, on = true, off = false, everything else not saved)
# - heating_target_temperature (list of climate entities, target temperature is saved)
# - state_float (list of entities, state is converted to float if possible. if not, no value saved)
# - db_passwd

class permanent_recorder(hass.Hass):

    def initialize(self):
        self.log("Permanent Logger started")
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        
        self.light_brightness: Set[str] = self.args.get("light_brightness", set())
        self.state_string: Set[str] = self.args.get("state_string", set())
        self.state_boolean: Set[str] = self.args.get("state_boolean", set())
        self.heating_target_temperature: Set[str] = self.args.get("heating_target_temperature", set())
        self.state_float: Set[str] = self.args.get("state_float", set())
        self.cover: Set[str] = self.args.get("cover", set())

        for entity in self.light_brightness:
            self.listen_state(self.light_brightness_changed, entity)
        for entity in self.state_string:
            self.listen_state(self.state_string_changed, entity)    
        for entity in self.state_boolean:
            self.listen_state(self.state_boolean_changed, entity)   
        for entity in self.heating_target_temperature:
            self.listen_state(self.heating_target_temperature_changed, entity, attribute = "temperature")    
        for entity in self.state_float:
            self.listen_state(self.state_float_changed, entity)
        for entity in self.cover:
            self.listen_state(self.cover_changed, entity, attribute = "current_position")
            self.listen_state(self.cover_changed, entity, attribute = "current_tilt_position")
    
    def light_brightness_changed(self, entity, attributes, old, new, kwargs):
        if new == "off":
            brightness = float(0)
        elif new == "on":
            brightness = float(100)
        else:
            return
        try:
            brightness = self.byte_to_pct(self.get_state(entity, attribute="brightness"))
        except:
            pass
        self.client.write_points([{"measurement":entity,"fields":{"brightness":brightness}}])

    def state_string_changed(self, entity, attributes, old, new, kwargs):
        self.client.write_points([{"measurement":entity,"fields":{"state_string":str(new)}}])

    def state_boolean_changed(self, entity, attributes, old, new, kwargs):
        if new == "off":
            value = False
        elif new == "on":
            value = True
        else:
            return
        self.client.write_points([{"measurement":entity,"fields":{"state_boolean":value}}])

    def heating_target_temperature_changed(self, entity, attributes, old, new, kwargs):
#        if new == old:
#            return
        try:
            temperature_float = float(new)
        except:
            return
        self.client.write_points([{"measurement":entity,"fields":{"temperature":temperature_float}}])

    def state_float_changed(self, entity, attributes, old, new, kwargs):
        try:
            value_float = float(new)
        except:
            return
        self.client.write_points([{"measurement":entity,"fields":{"state_float":value_float}}])

    def cover_changed(self, entity, attributes, old, new, kwargs):
        try:
            position_float = float(self.get_state(entity, attribute="current_position"))
            tilt_float = float(self.get_state(entity, attribute="current_tilt_position"))
        except:
            return
        self.client.write_points([{"measurement":entity,"fields":{"position":position_float,"tilt":tilt_float}}])

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
    
#    def drop(self):
#        self.log("Drop Test 1")
#        self.client.drop_measurement("Test-Entity2")
#        self.log("Drop Test 1 done")
        
        
