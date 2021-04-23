import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
import datetime

# Calculate Energy consumption and costs from power data and write it to influxdb
#
# Args:
#  price_per_kWh: 0.2809
#  db_passwd: !secret permanent_db_passwd
#  db_field: state_float
#  #save_measurement_name: energy_consumption_daily (if not provided, energy_consumption_test will be used)
#  #special_date: "2020-09-30" (if provided, at app start this date will be calculated and saved to database. please remove after that one-time-calculation)
#  db_measurement_total_kWh: sensor.stromzaehler_netzbezug (measured total consumption from power meter)


class energy_consumption_and_costs(hass.Hass):

    def initialize(self):
        self.run_in(self.initialize_delayed,12)
    
    def initialize_delayed(self, kwargs):
        # define daily time to run the calculation:
        time_daily_calculation =  datetime.time(3, 50, 43)
        time_daily_message =  datetime.time(4, 35, 43)
        # initialize database stuff
        self.host = self.args.get("db_host", "a0d7b954-influxdb")
        self.port=8086
        self.user = self.args.get("db_user", "appdaemon")
        self.password = self.args.get("db_passwd", None)
        self.db_name = self.args.get("db_name", "homeassistant_permanent")
        self.db_field = self.args.get("db_field", "state_float")
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.db_name)
        self.save_measurement_name = self.args.get("save_measurement_name", "energy_consumption_test")
        self.ad_namespace = "ad_namespace"
        self.sensor_name_consumption_total = self.args.get("sensor_name_consumption_total", "sensor.el_leistung_verbrauch_gesamt")
        special_date = self.args.get("special_date", None)
        # restore sensors in HA
        self.reset_all_sensors_in_ad_namespace()
        self.restore_sensors_in_ha()
        # calculate for a given single date
        if special_date is not None:
            self.calculate_energy_consumption_and_costs(special_date)
        # testing

        # run daily
        self.run_daily(self.generate_data_for_yesterday, time_daily_calculation)
        self.generate_data_for_yesterday(None) # Caution! Will lead to double values, if used additionally to daily calculation!

        # drop some measurements from testing
        #self.drop("sensor.test_measurement")
        
        
    def generate_data_for_yesterday(self, kwargs):
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        #today_str = (datetime.datetime.now()).strftime('%Y-%m-%d')
        self.log("running consumption calclulation for " + yesterday_str)
        self.calculate_energy_consumption_and_costs(yesterday_str)
        #consumption_kWh_total, total_consumption_cost, known_consumption_kWh_total, known_consumption_costs, unknown_consumption_kWh, unknown_consumers_cost, details_dict = self.calculate_energy_consumption(today_str)
        #message_text = "Verbrauch gestern: {} kWh => {} €\n\nVerbrauch im Detail:\n".format(round(consumption_kWh_total,1),round(total_consumption_cost,2))
        #details_sorted = sorted(details_dict.items(), key=lambda x: x[1], reverse=True)
        #for i in details_sorted:
        #    message_text = message_text + "\n{}: {} kWh => {} €".format(i[0],round(i[1],1),round(i[1]*self.price_per_kWh,2))
        #if unknown_consumption_kWh >= 0:
        #    message_text = message_text + "\n\nunbekannte Verbraucher: {} kWh => {} €".format(round(unknown_consumption_kWh,1),round(unknown_consumers_cost,2))
        #else:
        #    message_text = message_text + "\n\nZugeordneter Stromverbrauch größer als tatsächlicher. Leistungsfaktoren anpassen!"
        #if consumption_kWh_total > 0:
        #    message_text = message_text + "\n\n{} % vom Stromverbrauch sind zugeordnet".format(int(round(100*known_consumption_kWh_total/consumption_kWh_total,0)))
        #self.fire_event("custom_notify", message=message_text, target="telegram_jo")
        # temporary section for power factor:
#        self.fire_event("custom_notify", message=text_cos_phi, target="telegram_jo")
        
        

    def calculate_energy_consumption_and_costs(self, date_str):
        ts_start_calculation = datetime.datetime.now().timestamp()
        ts_start_calculation_total = datetime.datetime.now().timestamp()
        self.price_per_kWh_without_pv = float(self.get_state(self.args.get("input_number_entity_price_per_kwh", "input_number.strompreis")))
        
        # time and date stuff
        ts_start_local = datetime.datetime.strptime(date_str + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_start_local_ns = ts_start_local  * 1e9
        ts_start_local_ns_plus_buffer = ts_start_local_ns - 12*3600*1e9 # +12 hours for query to know value before that day started
        ts_end_local = datetime.datetime.strptime(date_str + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_end_local_ns = ts_end_local * 1e9 + 999
        ts_save_local_ns = datetime.datetime.strptime(date_str + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
        utc_offset_timestamp = datetime.datetime.now().timestamp() - datetime.datetime.utcnow().timestamp()
        date_next_day_str = (datetime.datetime.strptime(date_str + 'T12:00:00.0', '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(1)).strftime('%Y-%m-%d')
        if date_next_day_str[8:10] == "01":
            month_finished = True
        else:
            month_finished = False
        if date_next_day_str[5:10] == "01-01":
            calendar_year_finished = True
        else:
            calendar_year_finished = False
        if date_next_day_str[5:10] == "07-01":
            winter_year_finished = True
        else:
            winter_year_finished = False
            
        # load prices PV effective from db
        query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, self.args["db_measurement_price_pv_effective"], int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        price_pv_effective_points = self.client.query(query).get_points()
        price_pv_effective_timestrings = []
        price_pv_effective_timestamps = []
        price_pv_effective_values = []
        for point in price_pv_effective_points:
            timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
            if timestamp_local < ts_start_local:
                break
            price_pv_effective_timestamps.append(timestamp_local)
            price_pv_effective_timestrings.append(point["time"])
            price_pv_effective_values.append(point[self.db_field])
        price_pv_effective_timestamps.append(ts_start_local - utc_offset_timestamp - 300)
        price_pv_effective_timestrings.append(datetime.datetime.fromtimestamp(ts_start_local - utc_offset_timestamp - 300).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        price_pv_effective_values.append(self.price_per_kWh_without_pv)
        
        # load prices PV invoice from db
        query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, self.args["db_measurement_price_pv_invoice"], int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        price_pv_invoice_points = self.client.query(query).get_points()
        price_pv_invoice_timestrings = []
        price_pv_invoice_timestamps = []
        price_pv_invoice_values = []
        for point in price_pv_invoice_points:
            timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
            if timestamp_local < ts_start_local:
                break
            price_pv_invoice_timestamps.append(timestamp_local)
            price_pv_invoice_timestrings.append(point["time"])
            price_pv_invoice_values.append(point[self.db_field])
        price_pv_invoice_timestamps.append(ts_start_local - utc_offset_timestamp - 300)
        price_pv_invoice_timestrings.append(datetime.datetime.fromtimestamp(ts_start_local - utc_offset_timestamp - 300).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        price_pv_invoice_values.append(self.price_per_kWh_without_pv)
        self.log("Time for finding prices: {}".format(datetime.datetime.now().timestamp() - ts_start_calculation))
        
        # calculate for each power sensor
        consumption_kWh_known = 0.0
        cost_without_pv_known = 0.0
        cost_effective_known = 0.0 
        cost_invoice_known = 0.0
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            ts_start_calculation = datetime.datetime.now().timestamp()
            # load power values from db
            query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, sensor_power, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
            measurement_points = self.client.query(query).get_points()
            consumption_Ws = 0.0
            cost_effective = 0.0
            cost_invoice = 0.0
            past_timestep = ts_end_local
            start_time_reached = False
            for point in measurement_points:
                timestamp_local = datetime.datetime.strptime(point["time"], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() + utc_offset_timestamp
                if timestamp_local < ts_start_local:
                    timestamp_local = ts_start_local
                    start_time_reached = True
                time_delta_s = past_timestep - timestamp_local
                energy_Ws = point[self.db_field] * time_delta_s
                price_pv_effective = self.find_value_by_timestamp(price_pv_effective_timestamps, price_pv_effective_values, timestamp_local)
                price_pv_invoice = self.find_value_by_timestamp(price_pv_invoice_timestamps, price_pv_invoice_values, timestamp_local)
                cost_effective = cost_effective + price_pv_effective * energy_Ws / 3600000
                cost_invoice = cost_invoice + price_pv_invoice * energy_Ws / 3600000
                consumption_Ws = consumption_Ws + energy_Ws
                past_timestep = timestamp_local
                if start_time_reached:
                    break
            consumption_kWh = consumption_Ws / 3600000
            cost_without_pv = consumption_kWh * self.price_per_kWh_without_pv
            if sensor_power == self.sensor_name_consumption_total:
                consumption_kWh_total = consumption_kWh
                cost_without_pv_total = cost_without_pv
                cost_effective_total = cost_effective
                cost_invoice_total = cost_invoice
            else:
                if not sensor_power in self.args["db_measurements_to_skip_for_calculating_sum"]:
                    consumption_kWh_known = consumption_kWh_known + consumption_kWh
                    cost_without_pv_known = cost_without_pv_known + cost_without_pv
                    cost_effective_known = cost_effective_known + cost_effective
                    cost_invoice_known = cost_invoice_known + cost_invoice
#            if cost_without_pv > 0:
#                cost_saved_by_pv_effective_percent = (1 - (cost_effective / cost_without_pv)) * 100
#                cost_saved_by_pv_invoice_percent = (1 - (cost_invoice / cost_without_pv)) * 100
#            else:
#                cost_saved_by_pv_effective_percent = 0.0
#                cost_saved_by_pv_invoice_percent = 0.0
#            if cost_saved_by_pv_effective_percent < 0.0:
#                cost_saved_by_pv_effective_percent = 0.0
#            if cost_saved_by_pv_invoice_percent < 0.0:
#                cost_saved_by_pv_invoice_percent = 0.0
            sensor_power_readable_name = self.args["sensor_names_readable"].get(sensor_power, sensor_power.replace("sensor.el_leistung_",""))
            #self.log("kWh: {}".format(consumption_kWh))
            #self.log("Cost without PV: {}".format(cost_without_pv))
            #self.log("Cost with PV, effective: {} saved {}%".format(cost_effective, round(cost_saved_by_pv_effective_percent,2)))
            #self.log("Cost with PV, invoice: {} saved {}%".format(cost_invoice, round(cost_saved_by_pv_invoice_percent,2)))
            self.log("Time for calculating consumption and costs for {}: {}".format(sensor_power_readable_name,datetime.datetime.now().timestamp() - ts_start_calculation))
            
            # Consumption and Costs are now calculated for that power sensor
            # add it to a consumption sensor now
            
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            attributes_updated = self.update_consumption_attributes(consumption_sensor_name, consumption_kWh, cost_without_pv, cost_effective, cost_invoice, month_finished, calendar_year_finished, winter_year_finished)
            
            # save all that stuff
            if self.args["do_consumption_calculation"]:
                self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated, namespace = self.ad_namespace)
                self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated)
                self.client.write_points([{"measurement":consumption_sensor_name,"fields":attributes_updated,"time":int(ts_save_local_ns)}])
        
        # calculate the unknown consumers
        consumption_kWh_unknown = consumption_kWh_total - consumption_kWh_known
        cost_without_pv_unknown = cost_without_pv_total - cost_without_pv_known
        cost_effective_unknown = cost_effective_total - cost_effective_known
        cost_invoice_unknown = cost_invoice_total - cost_invoice_known
        consumption_sensor_name = "sensor.stromverbrauch_unbekannte_verbraucher"
        attributes_updated = self.update_consumption_attributes(consumption_sensor_name, consumption_kWh_unknown, cost_without_pv_unknown, cost_effective_unknown, cost_invoice_unknown, month_finished, calendar_year_finished, winter_year_finished)
        # save all that stuff
        if self.args["do_consumption_calculation"]:
            self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated, namespace = self.ad_namespace)
            self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated)
            self.client.write_points([{"measurement":consumption_sensor_name,"fields":attributes_updated,"time":int(ts_save_local_ns)}])
        
        # how long did all that take?
        self.log("Time for calculating consumption and costs total: {}".format(datetime.datetime.now().timestamp() - ts_start_calculation_total))
    
    def update_consumption_attributes(self, consumption_sensor_name, consumption_kWh, cost_without_pv, cost_effective, cost_invoice, month_finished, calendar_year_finished, winter_year_finished):
        attributes_updated = dict()
        if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
            attributes = self.get_state(consumption_sensor_name, attribute="all", namespace = "ad_namespace")["attributes"]
            Verbrauch_gesamt = attributes["Verbrauch gesamt"]
            Verbrauch_dieser_Monat = attributes["Verbrauch dieser Monat"]
            Verbrauch_dieses_Kalenderjahr = attributes["Verbrauch dieses Kalenderjahr"]
            Verbrauch_dieses_Winterjahr = attributes["Verbrauch dieses Winterjahr"]
            Kosten_ohne_PV_gesamt = attributes["Kosten ohne PV gesamt"]
            Kosten_mit_PV_effektiv_gesamt = attributes["Kosten mit PV effektiv gesamt"]
            Kosten_mit_PV_Abrechnung_gesamt = attributes["Kosten mit PV Abrechnung gesamt"]
            Kosten_ohne_PV_dieser_Monat = attributes["Kosten ohne PV dieser Monat"]
            Kosten_mit_PV_effektiv_dieser_Monat = attributes["Kosten mit PV effektiv dieser Monat"]
            Kosten_mit_PV_Abrechnung_dieser_Monat = attributes["Kosten mit PV Abrechnung dieser Monat"]
            Kosten_ohne_PV_dieses_Kalenderjahr = attributes["Kosten ohne PV dieses Kalenderjahr"]
            Kosten_mit_PV_effektiv_dieses_Kalenderjahr = attributes["Kosten mit PV effektiv dieses Kalenderjahr"]
            Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr = attributes["Kosten mit PV Abrechnung dieses Kalenderjahr"]
            Kosten_ohne_PV_dieses_Winterjahr = attributes["Kosten ohne PV dieses Winterjahr"]
            Kosten_mit_PV_effektiv_dieses_Winterjahr = attributes["Kosten mit PV effektiv dieses Winterjahr"]
            Kosten_mit_PV_Abrechnung_dieses_Winterjahr = attributes["Kosten mit PV Abrechnung dieses Winterjahr"]
        else:
            Verbrauch_gesamt = 0.0
            Verbrauch_dieser_Monat = 0.0
            Verbrauch_dieses_Kalenderjahr = 0.0
            Verbrauch_dieses_Winterjahr = 0.0
            Kosten_ohne_PV_gesamt = 0.0
            Kosten_mit_PV_effektiv_gesamt = 0.0
            Kosten_mit_PV_Abrechnung_gesamt = 0.0
            Kosten_ohne_PV_dieser_Monat = 0.0
            Kosten_mit_PV_effektiv_dieser_Monat = 0.0
            Kosten_mit_PV_Abrechnung_dieser_Monat = 0.0
            Kosten_ohne_PV_dieses_Kalenderjahr = 0.0
            Kosten_mit_PV_effektiv_dieses_Kalenderjahr = 0.0
            Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr = 0.0
            Kosten_ohne_PV_dieses_Winterjahr = 0.0
            Kosten_mit_PV_effektiv_dieses_Winterjahr = 0.0
            Kosten_mit_PV_Abrechnung_dieses_Winterjahr = 0.0
        
        # calculate new attributes
        # consumption
        attributes_updated["Verbrauch gesamt"] = Verbrauch_gesamt + consumption_kWh
        if self.args.get("special_date", None) == None:
            attributes_updated["Verbrauch gestern"] = consumption_kWh
        if month_finished:
            attributes_updated["Verbrauch dieser Monat"] = 0.0
            attributes_updated["Verbrauch letzter Monat"] = Verbrauch_dieser_Monat + consumption_kWh
        else:
            attributes_updated["Verbrauch dieser Monat"] = Verbrauch_dieser_Monat + consumption_kWh
        if calendar_year_finished:
            attributes_updated["Verbrauch dieses Kalenderjahr"] = 0.0
            attributes_updated["Verbrauch letztes Kalenderjahr"] = Verbrauch_dieses_Kalenderjahr + consumption_kWh
        else:
            attributes_updated["Verbrauch dieses Kalenderjahr"] = Verbrauch_dieses_Kalenderjahr + consumption_kWh
        if winter_year_finished:
            attributes_updated["Verbrauch dieses Winterjahr"] = 0.0
            attributes_updated["Verbrauch letztes Winterjahr"] = Verbrauch_dieses_Winterjahr + consumption_kWh
        else:
            attributes_updated["Verbrauch dieses Winterjahr"] = Verbrauch_dieses_Winterjahr + consumption_kWh
        # costs
        attributes_updated["Kosten ohne PV gesamt"] = Kosten_ohne_PV_gesamt + cost_without_pv
        attributes_updated["Kosten mit PV effektiv gesamt"] = Kosten_mit_PV_effektiv_gesamt + cost_effective
        attributes_updated["Kosten mit PV Abrechnung gesamt"] = Kosten_mit_PV_Abrechnung_gesamt + cost_invoice
        if self.args.get("special_date", None) == None:
            attributes_updated["Kosten ohne PV gestern"] = cost_without_pv
            attributes_updated["Kosten mit PV effektiv gestern"] = cost_effective
            attributes_updated["Kosten mit PV Abrechnung gestern"] = cost_invoice
        if month_finished:
            attributes_updated["Kosten ohne PV dieser Monat"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieser Monat"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieser Monat"] = 0.0
            attributes_updated["Kosten ohne PV letzter Monat"] = Kosten_ohne_PV_dieser_Monat + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letzter Monat"] = Kosten_mit_PV_effektiv_dieser_Monat + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letzter Monat"] = Kosten_mit_PV_Abrechnung_dieser_Monat + cost_invoice
        else:
            attributes_updated["Kosten ohne PV dieser Monat"] = Kosten_ohne_PV_dieser_Monat + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieser Monat"] = Kosten_mit_PV_effektiv_dieser_Monat + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieser Monat"] = Kosten_mit_PV_Abrechnung_dieser_Monat + cost_invoice
        if calendar_year_finished:
            attributes_updated["Kosten ohne PV dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten ohne PV letztes Kalenderjahr"] = Kosten_ohne_PV_dieses_Kalenderjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letztes Kalenderjahr"] = Kosten_mit_PV_effektiv_dieses_Kalenderjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letztes Kalenderjahr"] = Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr + cost_invoice
        else:
            attributes_updated["Kosten ohne PV dieses Kalenderjahr"] = Kosten_ohne_PV_dieses_Kalenderjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieses Kalenderjahr"] = Kosten_mit_PV_effektiv_dieses_Kalenderjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieses Kalenderjahr"] = Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr + cost_invoice
        if winter_year_finished:
            attributes_updated["Kosten ohne PV dieses Winterjahr"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieses Winterjahr"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieses Winterjahr"] = 0.0
            attributes_updated["Kosten ohne PV letztes Winterjahr"] = Kosten_ohne_PV_dieses_Winterjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letztes Winterjahr"] = Kosten_mit_PV_effektiv_dieses_Winterjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letztes Winterjahr"] = Kosten_mit_PV_Abrechnung_dieses_Winterjahr + cost_invoice
        else:
            attributes_updated["Kosten ohne PV dieses Winterjahr"] = Kosten_ohne_PV_dieses_Winterjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieses Winterjahr"] = Kosten_mit_PV_effektiv_dieses_Winterjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieses Winterjahr"] = Kosten_mit_PV_Abrechnung_dieses_Winterjahr + cost_invoice
        return attributes_updated

    def find_value_by_timestamp(self, list_of_timestamps, list_of_values, timestamp):
        counter = 0
        for t in list_of_timestamps:
            if t <= timestamp:
                break
            else:
                counter += 1
        return list_of_values[counter]
    
    def get_ha_power_sensors_for_consumption_calculation(self):
        all_ha_sensors = self.get_state("sensor").keys()
        sensors_for_power_calculation = []
        for sensor_power in all_ha_sensors:
            if sensor_power.startswith("sensor.el_leistung_") and not "scheinleistung" in sensor_power and not sensor_power.startswith("sensor.el_leistung_berechnet_licht_") and not sensor_power in self.args["db_measurements_to_skip_for_consumption_calculation"]:
                sensors_for_power_calculation.append(sensor_power)
        return sensors_for_power_calculation
    
    def restore_sensors_in_ha(self):
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
                state_and_attributes = self.get_state(consumption_sensor_name, attribute="all", namespace = "ad_namespace")
                self.set_state(consumption_sensor_name, state = state_and_attributes["state"], attributes = state_and_attributes["attributes"])
        consumption_sensor_name = "sensor.stromverbrauch_unbekannte_verbraucher"
        if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
            state_and_attributes = self.get_state(consumption_sensor_name, attribute="all", namespace = "ad_namespace")
            self.set_state(consumption_sensor_name, state = state_and_attributes["state"], attributes = state_and_attributes["attributes"])
    
    def reset_all_sensors_in_ad_namespace(self):
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
                self.remove_entity(consumption_sensor_name, namespace = self.ad_namespace)
        consumption_sensor_name = "sensor.stromverbrauch_unbekannte_verbraucher"
        if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
            self.remove_entity(consumption_sensor_name, namespace = self.ad_namespace)
        
    def drop(self, measurement_name):
        self.client.drop_measurement(measurement_name)
