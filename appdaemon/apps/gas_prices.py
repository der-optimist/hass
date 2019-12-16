import appdaemon.plugins.hass.hassapi as hass
from typing import Set
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
                'ids': list_of_station_ids
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
            self.log("loaded")
            #self.log(r.content)
            #self.log(r.raw)
            self.log(r.text)
        else:
            # log http error. no second try here, as update will be done in a few minutes anyway
            self.log("downloading gas prices from tankerkoenig failed. http error {}".format(r.status_code))

