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
        self.sensor_rest_forecast = "sensor.solcast_forecast_rest"
        self.sensor_forecast_data_chart = "sensor.solcast_forecast_chart"
        self.listen_state(self.sensor_rest_forecast_changed, self.sensor_rest_forecast, attribute = "forecasts")
        try:
            current_forecasts = self.get_state(self.sensor_rest_forecast, attribute = "forecasts")
            self.sensor_rest_forecast_changed(self.sensor_rest_forecast, "forecasts", None, current_forecasts, None)
        except Exception as e:
            self.log("Error running forecast at startup. Error was {}".format(e))
 
    def sensor_rest_forecast_changed(self, entity, attribute, old, new, kwargs):
#        self.log("--- entity ---")
#        self.log(entity)
#        self.log("--- attribute ---")
#        self.log(attribute)
#        self.log("--- new ---")
#        self.log(new)
#        self.log("--- kwargs ---")
#        self.log(kwargs)
        timestamps = []
        forecast_values = []
        utc_offset = self.utc_offset(None)
        for forecast in new:
            end_time_string = forecast["period_end"][:26]
            timestamp = int((datetime.datetime.strptime(end_time_string, "%Y-%m-%dT%H:%M:%S.%f") - utc_offset).timestamp())
            value_watt = float(forecast["pv_estimate"]) * 1000
            timestamps.append(timestamp)
            forecast_values.append(value_watt)
        self.set_state(self.sensor_forecast_data_chart, state = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")), attributes = {"timestamps": timestamps, "forecast_values": forecast_values})
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
