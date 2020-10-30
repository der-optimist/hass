import appdaemon.plugins.hass.hassapi as hass
from typing import Set
from influxdb import InfluxDBClient
import datetime
#from statistics import median

# Calculate Energy consumption from power data and write it to influxdb
#
# Args:
#  price_per_kWh: 0.2809
#  db_passwd: !secret permanent_db_passwd
#  db_field: state_float
#  #save_measurement_name: energy_consumption_daily (if not provided, energy_consumption_test will be used)
#  #special_date: "2020-09-30" (if provided, at app start this date will be calculated and saved to database. please remove after that one-time-calculation)
#  db_measurement_total_kWh: sensor.stromzaehler_netzbezug (measured total consumption from power meter)
#  db_measurements_Watt: (dict, measurement name in db : readable name for notification)
#    sensor.el_leistung_backofen: Backofen
#  db_measurements_kWh: (dict, measurement name in db : readable name for notification)
#    sensor.stromzahler_kochfeld: Kochfeld
#  permanent_consumers: (dict, device and permanent consumption in W)
#    fritzbox: 13


class energy_consumption_daily(hass.Hass):

    def initialize(self):
        # define daily time to run the calculation:
        daily_time =  datetime.time(4, 35, 43)
        #daily_time =  datetime.time(10, 3, 0)
        # initialize database stuff
        self.host = self.args.get("host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.dbname = self.args.get("dbname", "homeassistant_permanent")
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        self.db_measurement_total_kWh = self.args["db_measurement_total_kWh"]
        self.db_measurements_Watt = self.args["db_measurements_Watt"]
        self.db_measurements_kWh = self.args["db_measurements_kWh"]
        self.permanent_consumers = self.args["permanent_consumers"]
        self.db_field: Set[str] = self.args.get("db_field", set())
        self.price_per_kWh = self.args.get("price_per_kWh", 0.0)
        self.save_measurement_name = self.args.get("save_measurement_name", "energy_consumption_test")
        special_date = self.args.get("special_date", None)
        # calculate for a given single date
        if special_date is not None:
            self.calculate_energy_consumption(special_date)
        # run daily
        self.run_daily(self.generate_data_for_yesterday, daily_time)
        # drop some measurements from testing
        #self.drop()
        
        
    def generate_data_for_yesterday(self, kwargs):
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        self.log("running consumption calclulation for " + yesterday_str)
        consumption_kWh_total, total_consumption_cost, known_consumption_kWh_total, known_consumption_costs, unknown_consumption_kWh, unknown_consumers_cost, details_dict, text_cos_phi = self.calculate_energy_consumption(yesterday_str)
        message_text = "Verbrauch gestern: {} kWh => {} €\n\nVerbrauch im Detail:\n".format(round(consumption_kWh_total,1),round(total_consumption_cost,2))
        details_sorted = sorted(details_dict.items(), key=lambda x: x[1], reverse=True)
        for i in details_sorted:
            message_text = message_text + "\n{}: {} kWh => {} €".format(i[0],round(i[1],1),round(i[1]*self.price_per_kWh,2))
        if unknown_consumption_kWh >= 0:
            message_text = message_text + "\n\nunbekannte Verbraucher: {} kWh => {} €".format(round(unknown_consumption_kWh,1),round(unknown_consumers_cost,2))
        else:
            message_text = message_text + "\n\nZugeordneter Stromverbrauch größer als tatsächlicher. Leistungsfaktoren anpassen!"
        if consumption_kWh_total > 0:
            message_text = message_text + "\n\n{} % vom Stromverbrauch sind zugeordnet".format(int(round(100*known_consumption_kWh_total/consumption_kWh_total,0)))
        self.fire_event("custom_notify", message=message_text, target="telegram_jo")
        # temporary section for power factor:
        self.fire_event("custom_notify", message=text_cos_phi, target="telegram_jo")
        
        

    def calculate_energy_consumption(self, date_str):
        known_consumption_kWh_total = 0
        details_dict = dict()
        ts_start_local = datetime.datetime.strptime(date_str + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_start_local_ns = ts_start_local  * 1e9
        ts_start_local_ns_plus_buffer = ts_start_local_ns - 12*3600*1e9 # +12 hours for query to know value before that day started
        ts_end_local = datetime.datetime.strptime(date_str + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_end_local_ns = ts_end_local * 1e9 + 999
        ts_save_local_ns = datetime.datetime.strptime(date_str + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        utc_offset_timestamp = datetime.datetime.now().timestamp() - datetime.datetime.utcnow().timestamp()
        # calculate from power logs in Watt
        for measurement in self.db_measurements_Watt.keys():
            if measurement.startswith("sensor."):
                sensor_name = measurement.split("sensor.")[1]
            else:
                sensor_name = measurement
            query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, measurement, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
            #self.log(query)
            result_points = self.client.query(query).get_points()
            consumption_Ws = 0.0
            past_timestep = ts_end_local
            start_time_reached = False
            for point in result_points:
                #self.log(point)
                timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
                #self.log("timestamp local: {}".format(timestamp_local))
                if timestamp_local < ts_start_local:
                    timestamp_local = ts_start_local
                    start_time_reached = True
                time_delta_s = past_timestep - timestamp_local
                #self.log("timedelta: {} s".format(time_delta_s))
                energy_Ws = point[self.db_field] * time_delta_s
                #self.log("energy: {} Ws".format(energy_Ws))
                consumption_Ws = consumption_Ws + energy_Ws
                past_timestep = timestamp_local
                if start_time_reached:
                    break
            consumption_kWh = consumption_Ws / 3600000
            cost = consumption_kWh * self.price_per_kWh
            self.log("Verbrauch {}: {} kWh, also {} EUR (berechnet aus Leistung)".format(sensor_name, round(consumption_kWh,2),round(cost,2)))
            # save to db
            self.client.write_points([{"measurement":self.save_measurement_name,"fields":{sensor_name:consumption_kWh},"time":int(ts_save_local_ns)}])
            details_dict[self.db_measurements_Watt.get(measurement,sensor_name)] = consumption_kWh
            known_consumption_kWh_total = known_consumption_kWh_total + consumption_kWh
        # calculate from consumption logs in kWh:
        for measurement in self.db_measurements_kWh.keys():
            if measurement.startswith("sensor."):
                sensor_name = measurement.split("sensor.")[1]
            else:
                sensor_name = measurement
            query_start = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_start_local_ns))
            counter_start_generator = result_points = self.client.query(query_start).get_points()
            for point in counter_start_generator:
                counter_start = point["last"]
            query_end = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_end_local_ns))
            counter_end_generator = result_points = self.client.query(query_end).get_points()
            for point in counter_end_generator:
                counter_end = point["last"]
            consumption_kWh = counter_end - counter_start
            cost = consumption_kWh * self.price_per_kWh
            self.log("Verbrauch {}: {} kWh, also {} EUR (berechnet aus Zaehlerstand)".format(sensor_name, round(consumption_kWh,2),round(cost,2)))
            # save to db
            self.client.write_points([{"measurement":self.save_measurement_name,"fields":{sensor_name:consumption_kWh},"time":int(ts_save_local_ns)}])
            details_dict[self.db_measurements_kWh.get(measurement,sensor_name)] = consumption_kWh
            known_consumption_kWh_total = known_consumption_kWh_total + consumption_kWh
        # calculate permanent consumers:
        permanent_consumers_watt = 0
        for consumer in self.permanent_consumers.keys():
            permanent_consumers_watt = permanent_consumers_watt + self.permanent_consumers.get(consumer)
        permanent_consumers_kWh = permanent_consumers_watt * 24 / 1000
        self.log("Dauerverbraucher: {} kWh, also {} EUR".format(round(permanent_consumers_kWh,1),round(permanent_consumers_kWh*self.price_per_kWh,2)))
        self.client.write_points([{"measurement":self.save_measurement_name,"fields":{"permanent_consumers":permanent_consumers_kWh},"time":int(ts_save_local_ns)}])
        details_dict["Dauerverbraucher {} W".format(int(round(permanent_consumers_watt,0)))] = permanent_consumers_kWh
        known_consumption_kWh_total = known_consumption_kWh_total + permanent_consumers_kWh
        # total consumption
        query_start = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, self.db_measurement_total_kWh, int(ts_start_local_ns))
        counter_start_generator = result_points = self.client.query(query_start).get_points()
        for point in counter_start_generator:
            counter_start = point["last"]
        query_end = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, self.db_measurement_total_kWh, int(ts_end_local_ns))
        counter_end_generator = result_points = self.client.query(query_end).get_points()
        for point in counter_end_generator:
            counter_end = point["last"]
        consumption_kWh_total = counter_end - counter_start
        total_consumption_cost = consumption_kWh_total * self.price_per_kWh
        self.log("Verbrauch gesamt (Stromzaehler): {} kWh, also {} EUR (berechnet aus Zaehlerstand)".format(round(consumption_kWh_total,1),round(total_consumption_cost,2)))
        self.client.write_points([{"measurement":self.save_measurement_name,"fields":{"total_consumption_power_meter":consumption_kWh_total},"time":int(ts_save_local_ns)}])
        unknown_consumption_kWh = consumption_kWh_total - known_consumption_kWh_total
        unknown_consumers_cost = unknown_consumption_kWh * self.price_per_kWh
        self.log("unbekannte Verbraucher: {} kWh, also {} EUR (berechnet aus Zaehlerstand)".format(round(unknown_consumption_kWh,1),round(unknown_consumers_cost,2)))
        self.client.write_points([{"measurement":self.save_measurement_name,"fields":{"unknown_consumers":unknown_consumption_kWh},"time":int(ts_save_local_ns)}])
        
        # temporary section for power facor
        # energy meter
        measurement = "sensor.sonoff_pow_r2_1_energie"
        query_start = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_start_local_ns))
        counter_start_generator = result_points = self.client.query(query_start).get_points()
        for point in counter_start_generator:
            counter_start = point["last"]
        query_end = 'SELECT last("{}") FROM "homeassistant_permanent"."autogen"."{}" WHERE time <= {}'.format(self.db_field, measurement, int(ts_end_local_ns))
        counter_end_generator = result_points = self.client.query(query_end).get_points()
        for point in counter_end_generator:
            counter_end = point["last"]
        consumption_kWh_from_kwh = counter_end - counter_start
        # apparent power
        measurement = "sensor.sonoff_pow_r2_1_scheinleistung"
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, measurement, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        #self.log(query)
        result_points = self.client.query(query).get_points()
        consumption_Ws = 0.0
        past_timestep = ts_end_local
        start_time_reached = False
        for point in result_points:
            #self.log(point)
            timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
            #self.log("timestamp local: {}".format(timestamp_local))
            if timestamp_local < ts_start_local:
                timestamp_local = ts_start_local
                start_time_reached = True
            time_delta_s = past_timestep - timestamp_local
            #self.log("timedelta: {} s".format(time_delta_s))
            energy_Ws = point[self.db_field] * time_delta_s
            #self.log("energy: {} Ws".format(energy_Ws))
            consumption_Ws = consumption_Ws + energy_Ws
            past_timestep = timestamp_local
            if start_time_reached:
                break
        consumption_apparentpower_from_W = consumption_Ws / 3600000
        # power
        measurement = "sensor.sonoff_pow_r2_1_wirkleistung"
        query = 'SELECT "{}" FROM "homeassistant_permanent"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, measurement, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        #self.log(query)
        result_points = self.client.query(query).get_points()
        consumption_Ws = 0.0
        past_timestep = ts_end_local
        start_time_reached = False
        for point in result_points:
            #self.log(point)
            timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
            #self.log("timestamp local: {}".format(timestamp_local))
            if timestamp_local < ts_start_local:
                timestamp_local = ts_start_local
                start_time_reached = True
            time_delta_s = past_timestep - timestamp_local
            #self.log("timedelta: {} s".format(time_delta_s))
            energy_Ws = point[self.db_field] * time_delta_s
            #self.log("energy: {} Ws".format(energy_Ws))
            consumption_Ws = consumption_Ws + energy_Ws
            past_timestep = timestamp_local
            if start_time_reached:
                break
        consumption_power_from_W = consumption_Ws / 3600000
        cos_phi_day = consumption_power_from_W / consumption_apparentpower_from_W
        text_cos_phi = "Verbrauch aus kWh: {} kWh\nVerbrauch aus W: {} kWh\nScheinenergie: {} kWh\nmittlerer cos phi: {}".format(round(consumption_kWh_from_kwh,2),round(consumption_power_from_W,2),round(consumption_apparentpower_from_W,2),round(cos_phi_day,3))
        
        known_consumption_costs = known_consumption_kWh_total  * self.price_per_kWh
        self.log("Stromverbrauch von bekannten Dingen, {}: {} kWh, also {} EUR ".format(date_str, round(known_consumption_kWh_total,1),round(known_consumption_costs,2)))
        return consumption_kWh_total, total_consumption_cost, known_consumption_kWh_total, known_consumption_costs, unknown_consumption_kWh, unknown_consumers_cost, details_dict, text_cos_phi
            


    
    def drop(self):
        self.client.drop_measurement("test_heating_controller_ez")
