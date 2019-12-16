import appdaemon.plugins.hass.hassapi as hass
from typing import Set
import re
import requests, io
import json
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
        self.load_prices(None)
        #self.run_every(self.load_prices, datetime.datetime.now(), 5 * 60) # update every 5 minutes


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
                station_name_ = re.sub("[!@#$%^&*()[]{};:,./<>?\|`~-=_+äöüßÄÖÜ]", "", station_name)
                self.log(station_name_)
                diesel = data_json['prices'][station_id]['diesel']
                e5 = data_json['prices'][station_id]['e5']
                self.log(e5)
                self.log(type(diesel))
                self.set_state("diesel_{}".format(station_name_), state = diesel, attributes = {"friendly_name": "Diesel - {}".format(station_name), "icon": "mdi:gas-station"})

            
        else:
            # log http error. no second try here, as update will be done in a few minutes anyway
            self.log("downloading gas prices from tankerkoenig failed. http error {}".format(r.status_code))

