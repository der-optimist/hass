import appdaemon.plugins.hass.hassapi as hass
import mysql.connector

# Saves a state or an attribute to a mysql db (like recorder, but less data => permanent)
#
# Args:
# - light_brightness (list of light entities, brightness is saved. on/off lights = 100%/0%)
# - state (list of entities, state is saved)
# - heating_target_temperature (list of climate entities, target temperature is saved)

class permanent_recorder(hass.Hass):

    def initialize(self):
        self.log("Permanent Logger started")
