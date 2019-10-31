import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient

# Saves a state or an attribute to a mysql db (like recorder, but less data => permanent)
#
# Args:
# - light_brightness (list of light entities, brightness is saved. on/off lights = 100%/0%)
# - state (list of entities, state is saved)
# - heating_target_temperature (list of climate entities, target temperature is saved)
# - db_passwd

class permanent_recorder(hass.Hass):

    def initialize(self):
        self.log("Permanent Logger started")
        self.host = self.args.get("host", "core-mariadb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        
        self.write_test1()
        self.write_test2()
        self.query_test()
        
    def write_test1(self):
        self.log("Write Test 1")
        self.client.write("Test-Entity brightness=25", protocol='line')
        self.log("Write Test 1 done")
        
    def write_test2(self):
        self.log("Write Test 2")
        self.client.write("Test-Entity brightness=on", protocol='line')
        self.log("Write Test 2 done")
