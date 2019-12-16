import appdaemon.plugins.hass.hassapi as hass
from typing import Set
import requests
import datetime

#
# What it does:
#   - Load gas prices from tankerkoenig and add HA sensors for e5 and diesel
# What args it needs:
#   - tankerkoenig_api_key
#   - stations => a dict of stations (id:name_to_show)

class gas_prices(hass.Hass):

    def initialize(self):
        self.base_url = "https://creativecommons.tankerkoenig.de/json/prices.php"
        self.stations: Set[str] = self.args.get("stations", set())
        list_of_station_ids = []
        for station in self.stations:
            list_of_station_ids.append(station)
        self.url_params = {
                'apikey': self.args["tankerkoenig_api_key"],
                'ids': ",".join(map(str, list_of_station_ids))
                }
        self.update_interval_minutes = 5 # minutes
        for i in range(1,60,self.update_interval_minutes):
            self.run_hourly(self.load_prices, datetime.time(hour=0, minute=i, second=12))
        self.load_prices(None)

    def load_prices(self, kwargs):
        try:
            r = requests.get(self.base_url, params = self.url_params)
        except:
            # catch connection error - r does not get a status code then
            self.log("Error while loading gas prices from tankerkoenig. Maybe connection problem")
            return
        if r.status_code == 200:
            self.log(r.text)
            data_json = r.json()
            for station_id in data_json['prices']:
                station_name = self.stations[station_id]
                station_name_ = station_name.replace(' ','_').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('Ä','Ae').replace('Ö','Oe').replace('Ü','Ue').lower()
                self.log(station_name_)
                diesel = data_json['prices'][station_id]['diesel']
                e5 = data_json['prices'][station_id]['e5']
                e10 = data_json['prices'][station_id]['e10']
                status = data_json['prices'][station_id]['status']
                self.set_state("sensor.diesel_{}".format(station_name_), state = diesel, attributes = {"friendly_name": "Diesel - {}".format(station_name), "icon": "mdi:gas-station"})
                self.set_state("sensor.e5_{}".format(station_name_), state = e5, attributes = {"friendly_name": "Super - {}".format(station_name), "icon": "mdi:gas-station"})
                self.set_state("sensor.e10_{}".format(station_name_), state = e10, attributes = {"friendly_name": "E10 - {}".format(station_name), "icon": "mdi:gas-station"})
                self.set_state("sensor.status_{}".format(station_name_), state = status, attributes = {"friendly_name": "Status - {}".format(station_name), "icon": "mdi:lock-clock"})
        else:
            # log http error. no second try here, as update will be done in a few minutes anyway
            self.log("downloading gas prices from tankerkoenig failed. http error {}".format(r.status_code))

