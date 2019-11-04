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
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        
        #self.drop()
        self.write_test1()
        self.write_test2()
        self.write_test3()
        self.write_test4()
#        self.query_test()
    
    def drop(self):
        self.log("Drop Test 1")
        self.client.drop_measurement("Test-Entity")
        self.log("Drop Test 1 done")
        
    def write_test1(self):
        self.log("Write Test 1")
        self.client.write_points([{"measurement":"Test-Entity2","fields":{"brightness":25}}])
        self.log("Write Test 1 done")
        
    def write_test2(self):
        self.log("Write Test 2")
        self.client.write_points([{"measurement":"Test-Entity2","fields":{"brightness":20}}])
        self.log("Write Test 2 done")
        
    def write_test3(self):
        self.log("Write Test 3")
        self.client.write_points([{"measurement":"Test-Entity2","fields":{"brightness":"on"}}])
        self.log("Write Test 3 done")

    def write_test4(self):
        self.log("Write Test 4")
        self.client.write_points([{"measurement":"Test-Entity2","fields":{"brightness":10}}])
        self.log("Write Test 4 done")
