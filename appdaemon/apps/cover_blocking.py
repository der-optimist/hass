import appdaemon.plugins.hass.hassapi as hass

#
# Manage Cover Blocking (First: Ice Alert)
#
# Args: see initialize()
# 

class cover_blocking(hass.Hass):

    def initialize(self):
        # Args
        self.outside_humidity_sensor = self.args["outside_humidity_sensor"]
        self.outside_temperature_sensor = self.args["outside_temperature_sensor"]
        self.ice_blocking_switch = self.args["ice_blocking_switch"]
        self.ice_blocking_automation_switch = self.args["ice_blocking_automation_switch"]
        self.rain_entity = self.args["rain_entity"]
        self.temp_blocking_rain = self.args["temp_blocking_rain"]
        self.temp_blocking_humidity = self.args["temp_blocking_humidity"]
        self.humidity_blocking = self.args["humidity_blocking"]
        self.temp_release = self.args["temp_release"]
        
        self.listen_state(self.check_if_blocking_needed, self.outside_humidity_sensor)
        self.listen_state(self.check_if_blocking_needed, self.outside_temperature_sensor)
        self.listen_state(self.check_if_blocking_needed, self.rain_entity)
        self.listen_state(self.ice_blocking_switch_changed, self.ice_blocking_switch)
        self.listen_state(self.position_jal_bad_og_changed,"cover.jalousie_bad_og", attribute = "current_position")
        self.listen_state(self.position_jal_gastezimmer_changed,"cover.jalousie_gastezimmer", attribute = "current_position")
        self.listen_state(self.position_jal_hst_changed,"cover.jalousie_hst", attribute = "current_position")
        self.listen_state(self.position_jal_kuche_changed,"cover.jalousie_kuche", attribute = "current_position")
        self.listen_state(self.position_jal_la_bodentiefes_changed,"cover.jalousie_la_bodentiefes", attribute = "current_position")
        self.listen_state(self.position_jal_la_lichtband_changed,"cover.jalousie_la_lichtband", attribute = "current_position")
        self.listen_state(self.position_jal_le_bodentiefes_changed,"cover.jalousie_le_bodentiefes", attribute = "current_position")
        self.listen_state(self.position_jal_le_lichtband_changed,"cover.jalousie_le_lichtband", attribute = "current_position")
        self.listen_state(self.position_jal_nahzimmer_changed,"cover.jalousie_nahzimmer", attribute = "current_position")
        self.listen_state(self.position_jal_schlafzimmer_changed,"cover.jalousie_schlafzimmer", attribute = "current_position")
        self.listen_state(self.position_jal_wz_bodentiefes_changed,"cover.jalousie_wz_bodentiefes", attribute = "current_position")
        self.listen_state(self.position_jal_wz_couch_changed,"cover.jalousie_wz_couch", attribute = "current_position")

    def check_if_blocking_needed(self, entity, attributes, old, new, kwargs):
        if self.get_state(self.ice_blocking_automation_switch) == "off":
            return
        try: 
            humidity = float(self.get_state(self.outside_humidity_sensor))
        except:
            self.log("Humidity Error: {} cannot be converted to float".format(self.get_state(self.outside_humidity_sensor)))
            return
        try: 
            temp = float(self.get_state(self.outside_temperature_sensor))
        except:
            self.log("Temperature Error: {} cannot be converted to float".format(self.get_state(self.outside_temperature_sensor)))
            return
        try: 
            rain_status = self.get_state(self.rain_entity)
        except:
            self.log("Rain Status Error: {}".format(self.get_state(self.rain_entity)))
            return
        if (humidity > self.humidity_blocking and temp < self.temp_blocking_humidity) or (rain_status == "on" and temp < self.temp_blocking_rain):
            self.set_state(self.ice_blocking_switch,state="on")
            #self.log("ice blocking switch on")
        elif temp > 5:
            self.set_state(self.ice_blocking_switch,state="off")
            #self.log("ice blocking switch off")
        else:
            pass
            #self.log("do not change ice blocking switch")

    def check_if_cover_should_be_blocked(self, entity, blocking_entity):
        try:
            position = float(self.get_state(entity, attribute = "current_position"))
        except:
            self.log("position of cover {} not float, but {}".format(entity,self.get_state(entity, attribute = "current_position")))
            return
        if self.get_state(self.ice_blocking_switch) == "on":
            if position > 0:
                self.set_state(blocking_entity, state="on")
            else:
                self.set_state(blocking_entity, state="off")
        elif self.get_state(self.ice_blocking_switch) == "off":
            self.set_state(blocking_entity, state="off")

    def ice_blocking_switch_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_bad_og", "input_boolean.sperre_jal_ba_og")
        self.check_if_cover_should_be_blocked("cover.jalousie_gastezimmer", "input_boolean.sperre_jal_gz")
        self.check_if_cover_should_be_blocked("cover.jalousie_hst", "input_boolean.sperre_jal_hst")
        self.check_if_cover_should_be_blocked("cover.jalousie_kuche", "input_boolean.sperre_jal_ku")
        self.check_if_cover_should_be_blocked("cover.jalousie_la_bodentiefes", "input_boolean.sperre_jal_la_bodentiefes")
        self.check_if_cover_should_be_blocked("cover.jalousie_la_lichtband", "input_boolean.sperre_jal_la_lichtband")
        self.check_if_cover_should_be_blocked("cover.jalousie_le_bodentiefes", "input_boolean.sperre_jal_le_bodentiefes")
        self.check_if_cover_should_be_blocked("cover.jalousie_le_lichtband", "input_boolean.sperre_jal_le_lichtband")
        self.check_if_cover_should_be_blocked("cover.jalousie_nahzimmer", "input_boolean.sperre_jal_nz")
        self.check_if_cover_should_be_blocked("cover.jalousie_schlafzimmer", "input_boolean.sperre_jal_sz")
        self.check_if_cover_should_be_blocked("cover.jalousie_wz_bodentiefes", "input_boolean.sperre_jal_wz_bodentiefes")
        self.check_if_cover_should_be_blocked("cover.jalousie_wz_couch", "input_boolean.sperre_jal_wz_couch")
        
    def position_jal_bad_og_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_bad_og", "input_boolean.sperre_jal_ba_og")
        
    def position_jal_gastezimmer_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_gastezimmer", "input_boolean.sperre_jal_gz")
        
    def position_jal_hst_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_hst", "input_boolean.sperre_jal_hst")
        
    def position_jal_kuche_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_kuche", "input_boolean.sperre_jal_ku")
        
    def position_jal_la_bodentiefes_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_la_bodentiefes", "input_boolean.sperre_jal_la_bodentiefes")
        
    def position_jal_la_lichtband_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_la_lichtband", "input_boolean.sperre_jal_la_lichtband")
        
    def position_jal_le_bodentiefes_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_le_bodentiefes", "input_boolean.sperre_jal_le_bodentiefes")
        
    def position_jal_le_lichtband_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_le_lichtband", "input_boolean.sperre_jal_le_lichtband")
        
    def position_jal_nahzimmer_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_nahzimmer", "input_boolean.sperre_jal_nz")
        
    def position_jal_schlafzimmer_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_schlafzimmer", "input_boolean.sperre_jal_sz")
        
    def position_jal_wz_bodentiefes_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_wz_bodentiefes", "input_boolean.sperre_jal_wz_bodentiefes")
        
    def position_jal_wz_couch_changed(self, entity, attributes, old, new, kwargs):
        self.check_if_cover_should_be_blocked("cover.jalousie_wz_couch", "input_boolean.sperre_jal_wz_couch")
