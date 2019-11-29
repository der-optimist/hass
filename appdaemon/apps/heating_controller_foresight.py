import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient

# Calculates derivation of room temp and increases/lowers target temp. accordingly
# (kind of adding a D part to a PI controller)
#
# Args:
# - db_passwd
# - db_measurement
# - db_field

class heating_controller_foresight(hass.Hass):

    def initialize(self):
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        
        self.client =InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        
        self.db_measurement: Set[str] = self.args.get("db_measurement", set())
        self.db_field: Set[str] = self.args.get("db_field", set())
        
        self.calc_derivation(None)
    
    def calc_derivation(self, kwargs):
        current_value = self.get_state("sensor.temp_esszimmer_taster")
        for hour in range(1,9):
            query = 'SELECT last("state_float") FROM "homeassistant_permanent"."autogen"."sensor.temp_esszimmer_taster" WHERE time > now() - 24h AND time < now() - {}h'.format(hour)
            self.log(query)
            historic_value = self.client.query(query)
            self.log(historic_value)
            derivative = (historic_value - current_value) / hour
            self.log(derivative)
