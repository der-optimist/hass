import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# App does:
#  - Calculate "real" electricity meter value from KNX pulse counter (to kWh)
#  - Create Sensor with this value
#  - Calculate power in W (from previous to current event)
#
# Args:
# offset_kwh = Offset for electricity sensor
# input_number_raw_value_persistent = an input number: input_number.xyz
# knx_counter = "sensor.stromzahler_xyz_rohdaten"
# ha_electricity_sensor_name = "sensor.stromzahler_xyz"
# ha_electricity_sensor_friendly_name = "Stromzähler XYZ"
# ha_power_sensor_name = "sensor.el_leistung_xyz"
# ha_power_sensor_friendly_name = "El. Leistung XYZ"
# phases: 1 or 3 (for checking plausibility)
# energy_per_pulse = 0.0005 (in kWh => 2000 pulses per kWh => 0.0005 kWh/pulse)
# knx_sending_every = 5 (expect to receive a new value after 10 pulses. Used only for calulating ramp-down values)
# cut_power_below: 10 (set to 0 if ramp-down goes below this value)
#

class counter_to_power_meter(hass.Hass):

    def initialize(self):
        # wait for KNX entities 
        self.run_in(self.initialize_delayed,30)
        
    def initialize_delayed(self, kwargs):
        try:
            self.max_plausible_watt_per_phase = 7360 # would be 32A @ 230V
            # initialize internal variables
            self.time_of_last_event = None
            self.value_of_last_event = None
            self.handle_ramp_down_timer = None
            self.offset_kwh = self.args["offset_kwh"]
            # persistent stuff
            self.raw_value_persistent = round(float(self.get_state(self.args["input_number_raw_value_persistent"])))
            self.log("current persistent raw value is {}".format(self.raw_value_persistent))
            self.raw_value_knx = round(float(self.get_state(self.args["knx_counter"])))
            self.log("current knx value is {}".format(self.raw_value_knx))
            self.raw_value_offset_persistent_to_knx = self.raw_value_persistent - self.raw_value_knx
            self.log("self.raw_value_offset_persistent_to_knx is {}".format(self.raw_value_offset_persistent_to_knx))
            if self.raw_value_offset_persistent_to_knx < 0:
                self.log("last saved persistent value below knx value. will update persistent value")
                self.raw_value_persistent = self.raw_value_knx
                self.raw_value_offset_persistent_to_knx = 0
                self.set_value(self.args["input_number_raw_value_persistent"], self.raw_value_persistent)
                self.log("updated self.raw_value_persistent so {}".format(self.raw_value_persistent))
                self.log("self.raw_value_offset_persistent_to_knx is {}".format(self.raw_value_offset_persistent_to_knx))
            # set states
            self.set_state(self.args["ha_electricity_sensor_name"], state = round(((self.raw_value_persistent * self.args["energy_per_pulse"]) + self.offset_kwh),3), attributes={"icon":"mdi:counter", "friendly_name": self.args["ha_electricity_sensor_friendly_name"], "unit_of_measurement": "kWh"})
            self.set_state(self.args["ha_power_sensor_name"], state = 0.0, attributes={"icon":"mdi:speedometer", "friendly_name": self.args["ha_power_sensor_friendly_name"], "unit_of_measurement": "W", "device_class": "power"})
            # listen for new values
            self.listen_state(self.counter_changed, self.args["knx_counter"])
        except Exception as e:
            self.log("Error during initializing. Will try again in 5 Minutes. Error was {}".format(e))
            self.run_in(self.initialize_delayed,300)

    def counter_changed(self, entity, attribute, old, new, kwargs):
        if new == "unavailable" or new == "Nicht verfügbar" or new == old:
            return
        if self.handle_ramp_down_timer != None:
            self.cancel_timer(self.handle_ramp_down_timer)
        current_time = datetime.datetime.now() # for most accurate value, capture current time first
        # check if raw value is higher than last saved persistent value (can be 0 when knx device rebooted)
        #self.log("debug: reveived new knx value {}. self.raw_value_offset_persistent_to_knx is {}".format(new,self.raw_value_offset_persistent_to_knx ))
        if (float(new) + self.raw_value_offset_persistent_to_knx) < self.raw_value_persistent:
            self.log("received raw value from knx lower than ast persistent value. will update internal offset")
            self.raw_value_offset_persistent_to_knx = self.raw_value_persistent - float(new) + self.args["knx_sending_every"]
        # Update electricity meter sensor
        self.raw_value_persistent = float(new) + self.raw_value_offset_persistent_to_knx
        #self.log("self.raw_value_persistent is {}".format(self.raw_value_persistent))
        new_electricity_value = (self.raw_value_persistent * self.args["energy_per_pulse"]) + self.offset_kwh
        #self.log("new_electricity_value is {}".format(new_electricity_value))
        attributes = self.get_state(self.args["ha_electricity_sensor_name"], attribute="all")["attributes"]
        self.set_state(self.args["ha_electricity_sensor_name"], state = round(new_electricity_value,3), attributes=attributes)
        self.set_value(self.args["input_number_raw_value_persistent"], self.raw_value_persistent)
        # calculate power
        if self.time_of_last_event == None:
            self.log("Looks like it is the first event since a restart. Power will be available next time")
        else:
            if self.value_of_last_event == None:
                self.log("I have a time of the last event, but no value... no idea how that can happen. Look for a bug!")
            else:
                time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
                electricity_delta_Ws = (self.raw_value_persistent - self.value_of_last_event) * self.args["energy_per_pulse"] * 3600 * 1000
                current_power = electricity_delta_Ws / time_delta_seconds
                if (current_power > (float(self.args["phases"]) * self.max_plausible_watt_per_phase)) or current_power < 0:
                    self.log("Unplausibler Wert fuer Leistung: {} Watt - werde ihn ignorieren".format(round(current_power, 1)))
                else:
                    if self.args["debug"] == True:
                        self.log("Gueltiger Wert fuer Leistung: {} Watt".format(round(current_power, 1)))
                    attributes = self.get_state(self.args["ha_power_sensor_name"], attribute="all")["attributes"]
                    self.set_state(self.args["ha_power_sensor_name"], state = round(current_power, 1), attributes=attributes)
                    #self.log("Value {} received from counter {}. Calculated new power value: {}".format(new,self.args["knx_counter"],round(current_power, 1)))
                    self.handle_ramp_down_timer = self.run_in(self.ramp_down,round(2 * time_delta_seconds + 1))
        # save current values in variables for next calculation
        self.time_of_last_event = current_time
        self.value_of_last_event = self.raw_value_persistent

    def ramp_down(self, kwargs):
        current_time = datetime.datetime.now() # for most accurate value, capture current time first
#        new_virtual_electricity_value = (self.value_of_last_event + self.args["knx_sending_every"]) * self.args["energy_per_pulse"]
        time_delta_seconds = (current_time - self.time_of_last_event).total_seconds()
        electricity_delta_Ws = self.args["knx_sending_every"] * self.args["energy_per_pulse"] * 3600 * 1000
        current_power = electricity_delta_Ws / time_delta_seconds
        if current_power < self.args["cut_power_below"]:
            attributes = self.get_state(self.args["ha_power_sensor_name"], attribute="all")["attributes"]
            self.set_state(self.args["ha_power_sensor_name"], state = 0.0, attributes=attributes)
            self.log("Rampdown limit of counter {} reached. Will set new power to 0".format(self.args["knx_counter"]))
        else:
            if self.args["debug"] == True:
                self.log("Ramp-Down Wert fuer Leistung: {} Watt".format(round(current_power, 1)))
            attributes = self.get_state(self.args["ha_power_sensor_name"], attribute="all")["attributes"]
            self.set_state(self.args["ha_power_sensor_name"], state = round(current_power, 1), attributes=attributes)
            #self.log("Rampdown set counter {} to new power value: {}".format(self.args["knx_counter"],round(current_power, 1)))
            self.handle_ramp_down_timer = self.run_in(self.ramp_down,round(time_delta_seconds + 0.5))
