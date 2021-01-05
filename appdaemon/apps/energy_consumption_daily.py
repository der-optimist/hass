import appdaemon.plugins.hass.hassapi as hass
import datetime

# Send Energy consumption daily
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

        self.sensor_consumption_total = self.args["sensor_consumption_total"]
        self.sensors_consumption_detail = self.args["sensors_consumption_detail"]
        self.price_per_kWh = self.args.get("price_per_kWh", 0.0)

        # run daily
        self.run_daily(self.calculate_yesterday, daily_time)
        self.calculate_yesterday(None) # for testing

        
        
    def calculate_yesterday(self, kwargs):
        yesterday_str = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        self.log("running consumption calclulation for " + yesterday_str)
        consumption_kWh_total = self.get_state(self.sensor_consumption_total)
        total_consumption_cost = consumption_kWh_total * self.price_per_kWh
        
        details_dict = dict()
        known_consumption_kWh = 0.0
        for sensor in self.sensors_consumption_detail.keys():
            consumption = self.get_state(sensor)
            known_consumption_kWh = known_consumption_kWh + consumption
            if consumption > 0.01:
                details_dict[self.sensors_consumption_detail.get(sensor)] = consumption
            
        unknown_consumption_kWh = consumption_kWh_total - known_consumption_kWh
        unknown_consumers_cost = unknown_consumption_kWh * self.price_per_kWh

        message_text = "Verbrauch gestern: {} kWh => {} €\n\nVerbrauch im Detail:\n".format(round(consumption_kWh_total,1),round(total_consumption_cost,2))
        details_sorted = sorted(details_dict.items(), key=lambda x: x[1], reverse=True)
        for i in details_sorted:
            message_text = message_text + "\n{}: {} kWh => {} €".format(i[0],round(i[1],1),round(i[1]*self.price_per_kWh,2))
        if unknown_consumption_kWh >= 0:
            message_text = message_text + "\n\nunbekannte Verbraucher: {} kWh => {} €".format(round(unknown_consumption_kWh,1),round(unknown_consumers_cost,2))
        else:
            message_text = message_text + "\n\nZugeordneter Stromverbrauch größer als tatsächlicher. Leistungsfaktoren anpassen!"
        if consumption_kWh_total > 0:
            message_text = message_text + "\n\n{} % vom Stromverbrauch sind zugeordnet".format(int(round(100*known_consumption_kWh/consumption_kWh_total,0)))
        self.fire_event("custom_notify", message=message_text, target="telegram_jo")
