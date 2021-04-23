import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient

# Calculate Energy consumption and costs from power data and write it to influxdb
#
# Args:


class test_ad(hass.Hass):
    
    def initialize(self):
        # initialize database stuff
        self.host = self.args.get("db_host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("db_user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.db_name = self.args.get("db_name", "homeassistant_permanent")
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.db_name)
        self.remove_old_sensors_from_db()

    def get_ha_power_sensors_for_consumption_calculation(self):
        all_ha_sensors = self.get_state("sensor").keys()
        sensors_for_power_calculation = []
        for sensor_power in all_ha_sensors:
            if sensor_power.startswith("sensor.el_leistung_") and not "scheinleistung" in sensor_power and not sensor_power.startswith("sensor.el_leistung_berechnet_licht_") and not sensor_power in self.args["db_measurements_to_skip_for_consumption_calculation"]:
                sensors_for_power_calculation.append(sensor_power)
        return sensors_for_power_calculation

    def remove_old_sensors_from_db(self):
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_") + "_vortag"
            self.drop(consumption_sensor_name)
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_") + "_vormonat"
            self.drop(consumption_sensor_name)
        
    def drop(self, measurement_name):
        self.client.drop_measurement(measurement_name)
