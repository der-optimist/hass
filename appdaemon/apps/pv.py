import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# What it does:
#   - 
# What args it needs:
#   - 
#  

class pv(hass.Hass):

    def initialize(self):
        # --- forecast ---
        sensor_rest_forecast = "sensor.solcast_forecast_rest"
        self.listen_state(self.sensor_rest_forecast_changed, sensor_rest_forecast, attribute = "forecasts")

 
    def sensor_rest_forecast_changed(self, entity, attribute, old, new, kwargs):
        self.log("--- entity ---")
        self.log(entity)
        self.log("--- attribute ---")
        self.log(attribute)
        self.log("--- new ---")
        self.log(new)
        self.log("--- kwargs ---")
        self.log(kwargs)
        utc_offset = self.utc_offset(None)
        self.log(utc_offset)
#        start_dt = (datetime.datetime.now() - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url
#        end_dt = (datetime.datetime.now() + datetime.timedelta(days=self.days_birthdays) - utc_offset).strftime("%Y-%m-%dT%H:%M:%S") # results in UTC time => "Z" in url


    def check_reminder(self, kwargs):
        pass

        
    def utc_offset(self, kwargs):
        now_utc_naive = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        now_loc_naive = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        utc_offset_dt = datetime.datetime.strptime(now_loc_naive, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(now_utc_naive, "%Y-%m-%dT%H:%M:%S")
        #self.log("utc offset: {}d {}sec".format(utc_offset_dt.days, utc_offset_dt.seconds))
        return utc_offset_dt
