import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Count HA entities
#
# Args: 
# 

class ha_overview(hass.Hass):

    def initialize(self):
        self.run_daily(self.calculate_overview, datetime.time(2, 45, 0))
        self.calculate_overview(None)

    def calculate_overview(self, kwargs):
        self.log("Will calculate HA info now")
        domains = {}
        total_count = 0
        for entity in self.get_state():
            domain = entity.split('.')[0]
            domain_count = domains.get(domain, 0)
            domain_count += 1
            total_count += 1
            domains[domain] = domain_count
        self.log(domains)
        self.log("Total: {}".format(total_count))
        
        attributes = {"friendly_name": "HA Entities", "icon": "mdi:counter", "unit_of_measurement":"Anzahl"}
        attributes.update(domains)
        self.set_state("sensor.ha_entities_overview", state = total_count, attributes = attributes)
