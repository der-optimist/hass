import appdaemon.plugins.hass.hassapi as hass

#
# App to switch an air dryer on and off depending on air humidity
#
# Args: see initialize()
# 

class air_dryer(hass.Hass):

    def initialize(self):
        # Args
        self.air_dryer_switch = self.args["air_dryer_switch"]
        self.energy_measurement_sensor = self.args["energy_measurement_sensor"]
        self.humidity_sensor = self.args["humidity_sensor"]
        self.humidity_standard_max = float(self.args["humidity_standard_max"])
        self.humidity_standard_min = float(self.args["humidity_standard_min"])
        self.humidity_special_max = float(self.args["humidity_special_max"])
        self.humidity_special_min = float(self.args["humidity_special_min"])
        self.zha_device_ieee = self.args["zha_device_ieee"]
        self.zha_device_command_time_1 = self.args["zha_device_command_time_1"]
        self.time_1_hours = int(self.args["time_1_hours"])
        self.zha_device_command_time_2 = self.args["zha_device_command_time_2"]
        self.time_2_hours = int(self.args["time_2_hours"])
        self.input_number_timer_special_humidity = self.args["input_number_timer_special_humidity"]
        
        self.listen_state(self.timer_state_changed, self.input_number_timer_special_humidity)
        self.listen_state(self.humidity_state_changed, self.humidity_sensor)
        self.listen_state(self.electrical_measurement_state_changed, self.energy_measurement_sensor)
        self.listen_event(self.button_time_1, "zha_event", device_ieee = self.zha_device_ieee, command = self.zha_device_command_time_1)
        self.listen_event(self.button_time_2, "zha_event", device_ieee = self.zha_device_ieee, command = self.zha_device_command_time_2)
        
        self.timer_handle = None
        self.time_internal_state = 0
        if not float(self.get_state(self.input_number_timer_special_humidity)) == float(0):
            self.log("Timer nicht Null als ich gestartet wurde, werde jetzt weiter runter zaehlen")
            self.special_mode = True
            self.stunde_abgelaufen(None)
        else:
            self.log("Timer ist Null als ich gestartet wurde, alles ruhig hier...")
            self.special_mode = False
    
    def timer_state_changed(self, entity, attributes, old, new, kwargs):
        self.log("State Change in Humidity Timer erkannt: {}".format(new))
        if round(float(new)) == 0:
            if self.time_internal_state == 0:
                self.log("Timer abgelaufen, werde jetzt auf normale Luftfeuchtigkeit umschalten")
                self.timer_handle = None
                self.special_mode = False
            else:
                self.log("Timer wurde wohl manuell auf 0 gestellt, breche den Timer ab")
                self.time_internal_state = 0
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                    self.timer_handle = None
                    self.special_mode = False
        else:
            if round(float(new)) == self.time_internal_state:
                self.log("Event wurde wohl durch mich selber ausgelöst weil eine Stunde um ist, werde eine neue Stunde timen...")
                self.timer_handle = self.run_in(self.stunde_abgelaufen,3600)
            else:
                self.log("Es wurde wohl eine neue Zeit eingestellt. Werde neuen Timer setzen")
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                self.time_internal_state = round(float(new))
                self.timer_handle = self.run_in(self.stunde_abgelaufen,3600)

    def humidity_state_changed(self, entity, attributes, old, new, kwargs):
        if self.special_mode:
            pass
            
    def electrical_measurement_state_changed(self, entity, attributes, old, new, kwargs):
        pass
        # Tank voll?
        
    def button_time_1(self,event_name,data,kwargs):
        self.time_internal_state = self.time_1_hours
        self.set_value(self.input_number_timer_special_humidity, self.time_1_hours)

    def button_time_2(self,event_name,data,kwargs):
        self.time_internal_state = self.time_2_hours
        self.set_value(self.input_number_timer_special_humidity, self.time_2_hours)

    def stunde_abgelaufen(self, kwargs):
        self.log("Eine Stunde ist wohl um")
        self.time_internal_state = self.time_internal_state - 1
        old_state = round(float(self.get_state(self.input_number_timer_special_humidity)))
        self.set_value(self.input_number_timer_special_humidity, old_state - 1)

