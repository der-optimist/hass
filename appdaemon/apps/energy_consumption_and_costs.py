import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
import datetime

# Calculate Energy consumption and costs from power data and write it to influxdb
#
# Args:


class energy_consumption_and_costs(hass.Hass):

    def initialize(self):
        self.run_in(self.initialize_delayed,22)
    
    def initialize_delayed(self, kwargs):
        # define daily time to run the calculation:
        time_daily_calculation =  datetime.time(3, 1, 2)
#        time_daily_message =  datetime.time(4, 35, 43)
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
        self.sensor_name_used_power_total = self.args.get("sensor_name_used_power_total", "sensor.el_leistung_verbrauch_gesamt")
        self.sensor_name_consumption_unknown = self.args.get("sensor_name_consumption_unknown", "sensor.stromverbrauch_unbekannte_verbraucher")
        special_date = self.args.get("special_date", None)
        # restore sensors in HA
        #self.reset_all_sensors_in_ad_namespace()# Caution! all consumption data in HA will be reset
        #self.reset_all_sensors_in_db() # Caution! all consumption data in DB will be lost!
        self.restore_sensors_in_ha()
        # calculate for a given single date
        if special_date is not None:
            self.prepare_data_for_energy_consumption_and_costs_calculation(special_date)
        # listen for external results
        self.listen_state(self.external_calculation_is_done, "input_boolean.stromverbrauch_ist_berechnet", new="on", old="off")
        # testing

        # run daily
        #self.run_daily(self.generate_data_for_yesterday, time_daily_calculation)
        #self.run_daily(self.send_message, time_daily_message)
        #self.send_message_for_yesterday(None)
        #self.generate_data_for_yesterday(None) # Caution! Will lead to double values, if used additionally to daily calculation!

        # drop some measurements from testing
        #self.drop("sensor.test_measurement")
    
    def generate_data_for_yesterday(self, kwargs):
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        #today_str = (datetime.datetime.now()).strftime('%Y-%m-%d')
        self.log("running consumption calclulation for " + yesterday_str)
        self.prepare_data_for_energy_consumption_and_costs_calculation(yesterday_str)

    def external_calculation_is_done(self, entity, attributes, old, new, kwargs):
        self.postprocess_data_for_energy_consumption_and_costs_calculation()
        
    def send_message(self, kwargs):
        consumption_known_entities = dict()
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            if not sensor_power in self.args["db_measurements_to_skip_for_calculating_sum"]:
                consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
                if self.entity_exists(consumption_sensor_name):
                    attributes = self.get_state(consumption_sensor_name, attribute="all")["attributes"]
                    if attributes["Verbrauch gestern"] > 0:
                        cost_saved_by_pv_invoice_percent = (1 - (attributes["Kosten mit PV Abrechnung gestern"] / attributes["Kosten ohne PV gestern"])) * 100
                    else:
                        cost_saved_by_pv_invoice_percent = 0.0
                    if cost_saved_by_pv_invoice_percent < 0.0:
                        cost_saved_by_pv_invoice_percent = 0.0
                    if sensor_power == self.sensor_name_used_power_total:
                        consumption_total = {"consumption_kWh":attributes["Verbrauch gestern"], "cost_without_pv":attributes["Kosten ohne PV gestern"], "cost_invoice":attributes["Kosten mit PV Abrechnung gestern"], "cost_saved_by_pv_invoice_percent": cost_saved_by_pv_invoice_percent}
                    else:
                        sorting_string = "{0:010.6f}".format(attributes["Verbrauch gestern"]) + "___" + consumption_sensor_name
                        consumption_known_entities[sorting_string] = {"name":sensor_power, "consumption_kWh":attributes["Verbrauch gestern"], "cost_without_pv":attributes["Kosten ohne PV gestern"], "cost_invoice":attributes["Kosten mit PV Abrechnung gestern"], "cost_saved_by_pv_invoice_percent": cost_saved_by_pv_invoice_percent}
        # total power
        consumption_sensor_name = self.sensor_name_used_power_total.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
        attributes = self.get_state(consumption_sensor_name, attribute="all")["attributes"]
        if attributes["Verbrauch gestern"] > 0:
            cost_saved_by_pv_invoice_percent = (1 - (attributes["Kosten mit PV Abrechnung gestern"] / attributes["Kosten ohne PV gestern"])) * 100
        else:
            cost_saved_by_pv_invoice_percent = 0.0
        if cost_saved_by_pv_invoice_percent < 0.0:
            cost_saved_by_pv_invoice_percent = 0.0
        consumption_total = {"consumption_kWh":attributes["Verbrauch gestern"], "cost_without_pv":attributes["Kosten ohne PV gestern"], "cost_invoice":attributes["Kosten mit PV Abrechnung gestern"], "cost_saved_by_pv_invoice_percent": cost_saved_by_pv_invoice_percent}
        # unknown power
        consumption_sensor_name = self.sensor_name_consumption_unknown
        attributes = self.get_state(consumption_sensor_name, attribute="all")["attributes"]
        if attributes["Verbrauch gestern"] > 0:
            cost_saved_by_pv_invoice_percent = (1 - (attributes["Kosten mit PV Abrechnung gestern"] / attributes["Kosten ohne PV gestern"])) * 100
        else:
            cost_saved_by_pv_invoice_percent = 0.0
        if cost_saved_by_pv_invoice_percent < 0.0:
            cost_saved_by_pv_invoice_percent = 0.0
        consumption_unknown = {"consumption_kWh":attributes["Verbrauch gestern"], "cost_without_pv":attributes["Kosten ohne PV gestern"], "cost_invoice":attributes["Kosten mit PV Abrechnung gestern"], "cost_saved_by_pv_invoice_percent": cost_saved_by_pv_invoice_percent}

        message_text = "Verbrauch gestern: {} kWh => {} € (-{}% bzw -{}€)\n\nVerbrauch im Detail:\n".format(round(consumption_total["consumption_kWh"],1),round(consumption_total["cost_invoice"],2),round(consumption_total["cost_saved_by_pv_invoice_percent"],0),round(consumption_total["cost_without_pv"] - consumption_total["cost_invoice"],2))
        for sorting_name in sorted(consumption_known_entities, reverse=True):
            if consumption_known_entities[sorting_name]["consumption_kWh"] > 0.1:
                sensor_power_readable_name = self.args["sensor_names_readable"].get(consumption_known_entities[sorting_name]["name"], consumption_known_entities[sorting_name]["name"].replace("sensor.el_leistung_",""))
                message_text = message_text + "\n{}:\n{} kWh => {} € (-{}% bzw -{}€)".format(sensor_power_readable_name, round(consumption_known_entities[sorting_name]["consumption_kWh"],1),round(consumption_known_entities[sorting_name]["cost_invoice"],2),round(consumption_known_entities[sorting_name]["cost_saved_by_pv_invoice_percent"],0),round((consumption_known_entities[sorting_name]["cost_without_pv"] - consumption_known_entities[sorting_name]["cost_invoice"]),2))
        if consumption_unknown["consumption_kWh"] >= 0:
            message_text = message_text + "\n\nunbekannte Verbraucher:\n{} kWh => {} € (-{}% bzw -{}€)".format(round(consumption_unknown["consumption_kWh"],1),round(consumption_unknown["cost_invoice"],2),round(consumption_unknown["cost_saved_by_pv_invoice_percent"],0),round(consumption_unknown["cost_without_pv"] - consumption_unknown["cost_invoice"],2))
        else:
            message_text = message_text + "\n\nZugeordneter Stromverbrauch größer als tatsächlicher. Leistungsfaktoren anpassen!"
        if consumption_total["consumption_kWh"] > 0:
            message_text = message_text + "\n\n{} % vom Stromverbrauch sind zugeordnet".format(int(round(100*(consumption_total["consumption_kWh"]-consumption_unknown["consumption_kWh"])/consumption_total["consumption_kWh"],0)))
        self.fire_event("custom_notify", message=message_text, target="telegram_jo")

    def prepare_data_for_energy_consumption_and_costs_calculation(self, date_str):
        ts_start_calculation_total = datetime.datetime.now().timestamp()
        self.price_per_kWh_without_pv = float(self.get_state(self.args.get("input_number_entity_price_per_kwh", "input_number.strompreis")))
        
        # time and date stuff
        ts_start_local = datetime.datetime.strptime(date_str + 'T00:00:00.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_start_local_ns = ts_start_local  * 1e9
        ts_start_local_ns_plus_buffer = ts_start_local_ns - 12*3600*1e9 # +12 hours for query to know value before that day started
        ts_end_local = datetime.datetime.strptime(date_str + 'T23:59:59.999999', '%Y-%m-%dT%H:%M:%S.%f').timestamp()
        ts_end_local_ns = ts_end_local * 1e9 + 999
        utc_offset_timestamp = datetime.datetime.now().timestamp() - datetime.datetime.utcnow().timestamp()
        
        f = open("/config/www/stromverbrauch/data.py", "w")
        f.write("date_str = '{}'\n".format(date_str))
        f.write("start_power = 0.0\n")
        f.write("start_price = {}\n".format(self.price_per_kWh_without_pv))
        f.write("db_field = '{}'\n".format(self.db_field))
        f.write("ts_start_local = {}\n".format(ts_start_local))
        f.write("ts_end_local = {}\n".format(ts_end_local))
        f.write("utc_offset_timestamp = {}\n".format(utc_offset_timestamp))
        
        # load prices PV effective from db
        query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, self.args["db_measurement_price_pv_effective"], int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        price_pv_effective_points = self.client.query(query).get_points()
        f.write("price_pv_effective_points = {}\n".format(list(price_pv_effective_points)))

        # load prices PV invoice from db
        query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, self.args["db_measurement_price_pv_invoice"], int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
        price_pv_invoice_points = self.client.query(query).get_points()
        f.write("price_pv_invoice_points = {}\n".format(list(price_pv_invoice_points)))
        
        # calculate for each power sensor
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        power_sensors = dict()
        for sensor_power in sensors_for_power_calculation:
            self.log(sensor_power)
            # load power values from db
            query = 'SELECT "{}" FROM "{}"."autogen"."{}" WHERE time >= {} AND time <= {} ORDER BY time DESC'.format(self.db_field, self.db_name, sensor_power, int(ts_start_local_ns_plus_buffer), int(ts_end_local_ns))
            measurement_points = self.client.query(query).get_points()
            power_sensors[sensor_power] = list(measurement_points)
        f.write("power_sensors = {}\n".format(power_sensors))
        f.close()
        # how long did all that take?
        self.log("Time for calculating consumption and costs total: {}".format(datetime.datetime.now().timestamp() - ts_start_calculation_total))
        
        # set todo flag for external calculation
        self.turn_on("input_boolean.stromverbrauch_todo")

    def postprocess_data_for_energy_consumption_and_costs_calculation(self):
        ts_start_calculation_total = datetime.datetime.now().timestamp()
        attributes = self.get_state("sensor.stromverbrauch_tag_extern_berechnet", attribute="all")["attributes"]
        dict_results = attributes["dict_results"]
        date_str = attributes["date_str"]
        
        # time and date stuff
        ts_save_local_ns = datetime.datetime.strptime(date_str + 'T23:59:59.0', '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1e9
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

        # calculate for each power sensor
        consumption_kWh_known = 0.0
        cost_without_pv_known = 0.0
        cost_effective_known = 0.0 
        cost_invoice_known = 0.0
        for sensor_power in dict_results.keys():
            self.log(sensor_power)

            consumption_kWh = dict_results[sensor_power]["consumption_kWh"]
            cost_without_pv = dict_results[sensor_power]["cost_without_pv"]
            cost_effective = dict_results[sensor_power]["cost_effective"]
            cost_invoice = dict_results[sensor_power]["cost_invoice"]
            if sensor_power == self.sensor_name_used_power_total:
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
#            sensor_power_readable_name = self.args["sensor_names_readable"].get(sensor_power, sensor_power.replace("sensor.el_leistung_",""))
            # add it to a consumption sensor now
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            attributes_updated, attributes_db = self.update_consumption_attributes(consumption_sensor_name, consumption_kWh, cost_without_pv, cost_effective, cost_invoice, month_finished, calendar_year_finished, winter_year_finished)
            
            # save all that stuff
            if self.args["do_consumption_calculation"]:
                self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated, namespace = self.ad_namespace)
                self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated)
                self.client.write_points([{"measurement":consumption_sensor_name,"fields":attributes_db,"time":int(ts_save_local_ns)}])
                
        # calculate the unknown consumers
        consumption_kWh_unknown = consumption_kWh_total - consumption_kWh_known
        cost_without_pv_unknown = cost_without_pv_total - cost_without_pv_known
        cost_effective_unknown = cost_effective_total - cost_effective_known
        cost_invoice_unknown = cost_invoice_total - cost_invoice_known
        consumption_sensor_name = self.sensor_name_consumption_unknown
        attributes_updated, attributes_db = self.update_consumption_attributes(consumption_sensor_name, consumption_kWh_unknown, cost_without_pv_unknown, cost_effective_unknown, cost_invoice_unknown, month_finished, calendar_year_finished, winter_year_finished)
        # save all that stuff
        if self.args["do_consumption_calculation"]:
            self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated, namespace = self.ad_namespace)
            self.set_state(consumption_sensor_name, state = attributes_updated["Verbrauch gesamt"], attributes = attributes_updated)
            self.client.write_points([{"measurement":consumption_sensor_name,"fields":attributes_db,"time":int(ts_save_local_ns)}])
        
        # how long did all that take?
        self.log("Time for calculating consumption and costs total: {}".format(datetime.datetime.now().timestamp() - ts_start_calculation_total))
        
        # reset "external calculation finished" flag
        self.turn_off("input_boolean.stromverbrauch_ist_berechnet")
        
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        if self.args.get("special_date", None) == None:
            self.send_message(None)
        else:
            self.fire_event("custom_notify", message="Stromverbrauch berechnet für {}".format(date_str), target="telegram_jo")

    def update_consumption_attributes(self, consumption_sensor_name, consumption_kWh, cost_without_pv, cost_effective, cost_invoice, month_finished, calendar_year_finished, winter_year_finished):
        attributes_updated = dict()
        attributes_db = dict()
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
        attributes_db["Verbrauch Tag"] = consumption_kWh
        if month_finished:
            attributes_updated["Verbrauch dieser Monat"] = 0.0
            attributes_updated["Verbrauch letzter Monat"] = Verbrauch_dieser_Monat + consumption_kWh
            attributes_db["Verbrauch Monat"] = Verbrauch_dieser_Monat + consumption_kWh
        else:
            attributes_updated["Verbrauch dieser Monat"] = Verbrauch_dieser_Monat + consumption_kWh
        if calendar_year_finished:
            attributes_updated["Verbrauch dieses Kalenderjahr"] = 0.0
            attributes_updated["Verbrauch letztes Kalenderjahr"] = Verbrauch_dieses_Kalenderjahr + consumption_kWh
            attributes_db["Verbrauch Kalenderjahr"] = Verbrauch_dieses_Kalenderjahr + consumption_kWh
        else:
            attributes_updated["Verbrauch dieses Kalenderjahr"] = Verbrauch_dieses_Kalenderjahr + consumption_kWh
        if winter_year_finished:
            attributes_updated["Verbrauch dieses Winterjahr"] = 0.0
            attributes_updated["Verbrauch letztes Winterjahr"] = Verbrauch_dieses_Winterjahr + consumption_kWh
            attributes_db["Verbrauch Winterjahr"] = Verbrauch_dieses_Winterjahr + consumption_kWh
        else:
            attributes_updated["Verbrauch dieses Winterjahr"] = Verbrauch_dieses_Winterjahr + consumption_kWh
        # costs
        attributes_updated["Kosten ohne PV gesamt"] = Kosten_ohne_PV_gesamt + cost_without_pv
        attributes_updated["Kosten mit PV effektiv gesamt"] = Kosten_mit_PV_effektiv_gesamt + cost_effective
        attributes_updated["Kosten mit PV Abrechnung gesamt"] = Kosten_mit_PV_Abrechnung_gesamt + cost_invoice
        attributes_updated["Einsparung durch PV gesamt"] = attributes_updated["Kosten ohne PV gesamt"] - attributes_updated["Kosten mit PV Abrechnung gesamt"]
        attributes_db["Kosten ohne PV gesamt"] = attributes_updated["Kosten ohne PV gesamt"]
        attributes_db["Kosten mit PV effektiv gesamt"] = attributes_updated["Kosten mit PV effektiv gesamt"]
        attributes_db["Kosten mit PV Abrechnung gesamt"] = attributes_updated["Kosten mit PV Abrechnung gesamt"]
        attributes_db["Einsparung durch PV gesamt"] = attributes_updated["Einsparung durch PV gesamt"]
        if self.args.get("special_date", None) == None:
            attributes_updated["Kosten ohne PV gestern"] = cost_without_pv
            attributes_updated["Kosten mit PV effektiv gestern"] = cost_effective
            attributes_updated["Kosten mit PV Abrechnung gestern"] = cost_invoice
            attributes_updated["Einsparung durch PV gestern"] = attributes_updated["Kosten ohne PV gestern"] - attributes_updated["Kosten mit PV Abrechnung gestern"]
        attributes_db["Kosten ohne PV Tag"] = cost_without_pv
        attributes_db["Kosten mit PV effektiv Tag"] = cost_effective
        attributes_db["Kosten mit PV Abrechnung Tag"] = cost_invoice
        attributes_db["Einsparung durch PV Tag"] = cost_without_pv - cost_invoice
        if month_finished:
            attributes_updated["Kosten ohne PV dieser Monat"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieser Monat"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieser Monat"] = 0.0
            attributes_updated["Einsparung durch PV dieser Monat"] = 0.0
            attributes_updated["Kosten ohne PV letzter Monat"] = Kosten_ohne_PV_dieser_Monat + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letzter Monat"] = Kosten_mit_PV_effektiv_dieser_Monat + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letzter Monat"] = Kosten_mit_PV_Abrechnung_dieser_Monat + cost_invoice
            attributes_updated["Einsparung durch PV letzter Monat"] = attributes_updated["Kosten ohne PV letzter Monat"] - attributes_updated["Kosten mit PV Abrechnung letzter Monat"]
            attributes_db["Kosten ohne PV Monat"] = attributes_updated["Kosten ohne PV letzter Monat"]
            attributes_db["Kosten mit PV effektiv Monat"] = attributes_updated["Kosten mit PV effektiv letzter Monat"]
            attributes_db["Kosten mit PV Abrechnung Monat"] = attributes_updated["Kosten mit PV Abrechnung letzter Monat"]
            attributes_db["Einsparung durch PV Monat"] = attributes_updated["Einsparung durch PV letzter Monat"]
        else:
            attributes_updated["Kosten ohne PV dieser Monat"] = Kosten_ohne_PV_dieser_Monat + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieser Monat"] = Kosten_mit_PV_effektiv_dieser_Monat + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieser Monat"] = Kosten_mit_PV_Abrechnung_dieser_Monat + cost_invoice
            attributes_updated["Einsparung durch PV dieser Monat"] = attributes_updated["Kosten ohne PV dieser Monat"] - attributes_updated["Kosten mit PV Abrechnung dieser Monat"]
        if calendar_year_finished:
            attributes_updated["Kosten ohne PV dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieses Kalenderjahr"] = 0.0
            attributes_updated["Einsparung durch PV dieses Kalenderjahr"] = 0.0
            attributes_updated["Kosten ohne PV letztes Kalenderjahr"] = Kosten_ohne_PV_dieses_Kalenderjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letztes Kalenderjahr"] = Kosten_mit_PV_effektiv_dieses_Kalenderjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letztes Kalenderjahr"] = Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr + cost_invoice
            attributes_updated["Einsparung durch PV letztes Kalenderjahr"] = attributes_updated["Kosten ohne PV letztes Kalenderjahr"] - attributes_updated["Kosten mit PV Abrechnung letztes Kalenderjahr"]
            attributes_db["Kosten ohne PV Kalenderjahr"] = attributes_updated["Kosten ohne PV letztes Kalenderjahr"]
            attributes_db["Kosten mit PV effektiv Kalenderjahr"] = attributes_updated["Kosten mit PV effektiv letztes Kalenderjahr"]
            attributes_db["Kosten mit PV Abrechnung Kalenderjahr"] = attributes_updated["Kosten mit PV Abrechnung letztes Kalenderjahr"]
            attributes_db["Einsparung durch PV Kalenderjahr"] = attributes_updated["Einsparung durch PV letztes Kalenderjahr"]
        else:
            attributes_updated["Kosten ohne PV dieses Kalenderjahr"] = Kosten_ohne_PV_dieses_Kalenderjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieses Kalenderjahr"] = Kosten_mit_PV_effektiv_dieses_Kalenderjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieses Kalenderjahr"] = Kosten_mit_PV_Abrechnung_dieses_Kalenderjahr + cost_invoice
            attributes_updated["Einsparung durch PV dieses Kalenderjahr"] = attributes_updated["Kosten ohne PV dieses Kalenderjahr"] - attributes_updated["Kosten mit PV Abrechnung dieses Kalenderjahr"]
        if winter_year_finished:
            attributes_updated["Kosten ohne PV dieses Winterjahr"] = 0.0
            attributes_updated["Kosten mit PV effektiv dieses Winterjahr"] = 0.0
            attributes_updated["Kosten mit PV Abrechnung dieses Winterjahr"] = 0.0
            attributes_updated["Einsparung durch PV dieses Winterjahr"] = 0.0
            attributes_updated["Kosten ohne PV letztes Winterjahr"] = Kosten_ohne_PV_dieses_Winterjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv letztes Winterjahr"] = Kosten_mit_PV_effektiv_dieses_Winterjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung letztes Winterjahr"] = Kosten_mit_PV_Abrechnung_dieses_Winterjahr + cost_invoice
            attributes_updated["Einsparung durch PV letztes Winterjahr"] = attributes_updated["Kosten ohne PV letztes Winterjahr"] - attributes_updated["Kosten mit PV Abrechnung letztes Winterjahr"]
            attributes_db["Kosten ohne PV Winterjahr"] = attributes_updated["Kosten ohne PV letztes Winterjahr"]
            attributes_db["Kosten mit PV effektiv Winterjahr"] = attributes_updated["Kosten mit PV effektiv letztes Winterjahr"]
            attributes_db["Kosten mit PV Abrechnung Winterjahr"] = attributes_updated["Kosten mit PV Abrechnung letztes Winterjahr"]
            attributes_db["Einsparung durch PV Winterjahr"] = attributes_updated["Einsparung durch PV letztes Winterjahr"]
        else:
            attributes_updated["Kosten ohne PV dieses Winterjahr"] = Kosten_ohne_PV_dieses_Winterjahr + cost_without_pv
            attributes_updated["Kosten mit PV effektiv dieses Winterjahr"] = Kosten_mit_PV_effektiv_dieses_Winterjahr + cost_effective
            attributes_updated["Kosten mit PV Abrechnung dieses Winterjahr"] = Kosten_mit_PV_Abrechnung_dieses_Winterjahr + cost_invoice
            attributes_updated["Einsparung durch PV dieses Winterjahr"] = attributes_updated["Kosten ohne PV dieses Winterjahr"] - attributes_updated["Kosten mit PV Abrechnung dieses Winterjahr"]
        return attributes_updated, attributes_db

#    def find_value_by_timestamp(self, list_of_timestamps, list_of_values, timestamp):
#        counter = 0
#        for t in list_of_timestamps:
#            if t <= timestamp:
#                break
#            else:
#                counter += 1
#        return list_of_values[counter]
    
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
        consumption_sensor_name = self.sensor_name_consumption_unknown
        if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
            state_and_attributes = self.get_state(consumption_sensor_name, attribute="all", namespace = "ad_namespace")
            self.set_state(consumption_sensor_name, state = state_and_attributes["state"], attributes = state_and_attributes["attributes"])
    
    def reset_all_sensors_in_ad_namespace(self):
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
                self.remove_entity(consumption_sensor_name, namespace = self.ad_namespace)
        consumption_sensor_name = self.sensor_name_consumption_unknown
        if self.entity_exists(consumption_sensor_name, namespace = self.ad_namespace):
            self.remove_entity(consumption_sensor_name, namespace = self.ad_namespace)

    def reset_all_sensors_in_db(self):
        sensors_for_power_calculation = self.get_ha_power_sensors_for_consumption_calculation()
        for sensor_power in sensors_for_power_calculation:
            consumption_sensor_name = sensor_power.replace("sensor.el_leistung_", "sensor.stromverbrauch_")
            self.drop(consumption_sensor_name)
        consumption_sensor_name = self.sensor_name_consumption_unknown
        self.drop(consumption_sensor_name)
        
    def drop(self, measurement_name):
        self.client.drop_measurement(measurement_name)
