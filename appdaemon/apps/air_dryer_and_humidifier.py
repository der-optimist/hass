import appdaemon.plugins.hass.hassapi as hass

#
# App to switch an air dryer or humidifier on and off depending on air humidity
#
# Args: see initialize()
# 

class air_dryer_and_humidifier(hass.Hass):

    def initialize(self):
        # Args
        self.machine_type = self.args["machine_type"] # dryer or humidifier
        self.zigbee = self.args["zigbee"]
        self.use_pv_power = self.args["use_pv_power"]
        self.air_dryer_or_humidifier_switch = self.args["air_dryer_or_humidifier_switch"]
        self.energy_measurement_sensor = self.args["energy_measurement_sensor"]
        self.humidity_sensor = self.args["humidity_sensor"]
        self.humidity_standard_max = float(self.args["humidity_standard_max"])
        self.humidity_standard_min = float(self.args["humidity_standard_min"])
        self.humidity_special_max = float(self.args["humidity_special_max"])
        self.humidity_special_min = float(self.args["humidity_special_min"])
        self.input_number_timer_special_humidity = self.args["input_number_timer_special_humidity"]
        self.name_reminder_switch_tank = self.args["name_reminder_switch_tank"]
        self.text_reminder_switch_tank = self.args["text_reminder_switch_tank"]
        if self.zigbee:
            self.zha_device_ieee = self.args["zha_device_ieee"]
            self.zha_device_command_time_1 = self.args["zha_device_command_time_1"]
            self.time_1_hours = int(self.args["time_1_hours"])
            self.zha_device_command_time_2 = self.args["zha_device_command_time_2"]
            self.time_2_hours = int(self.args["time_2_hours"])
        if self.use_pv_power:
            self.pv_power_for_step_1 = self.args["pv_power_for_step_1"]
            self.humidity_change_step_1 = self.args["humidity_change_step_1"]
        self.humidity_change_current = 0
        
        self.listen_state(self.timer_state_changed, self.input_number_timer_special_humidity)
        self.listen_state(self.humidity_state_changed, self.humidity_sensor)
        self.listen_state(self.electrical_measurement_state_changed, self.energy_measurement_sensor)
        if self.zigbee:
            self.listen_event(self.button_time_1, "zha_event", device_ieee = self.zha_device_ieee, command = self.zha_device_command_time_1)
            self.listen_event(self.button_time_2, "zha_event", device_ieee = self.zha_device_ieee, command = self.zha_device_command_time_2)
        if self.use_pv_power:
            self.listen_state(self.pv_power_changed, self.args["pv_power_sensor"])
        
        # define tank full reminder switch
        icon_reminder_tank = "/local/icons/reminders/drop_blue_blink.svg"
        self.attributes_reminder_tank = {"entity_picture": icon_reminder_tank, "friendly_name": self.text_reminder_switch_tank}
        self.set_state(self.name_reminder_switch_tank, state = "off", attributes = self.attributes_reminder_tank)
        
        self.timer_handle = None
        self.time_internal_state = 0
        if not float(self.get_state(self.input_number_timer_special_humidity)) == float(0):
            self.log("Timer nicht Null als ich gestartet wurde, werde jetzt weiter runter zaehlen")
            self.special_mode = True
            self.time_internal_state = round(float(self.get_state(self.input_number_timer_special_humidity)))
            self.timer_handle = self.run_in(self.stunde_abgelaufen,3600)
        else:
            self.log("Timer ist Null als ich gestartet wurde, alles ruhig hier...")
            self.special_mode = False
        
        self.initialize_when_ready(None)

        
    def initialize_when_ready(self, kwargs):
        # dryer_or_humidifier needed?
        try:
            self.current_humidity = float(self.get_state(self.humidity_sensor))
        except:
            self.run_in(self.initialize_when_ready,61)
            self.log("Humidity Sensor not ready. Will try again later.")
            return
        self.log("Humidity Sensor ready. Value is {}".format(self.current_humidity))
        
        try:
            el_power = float(self.get_state(self.energy_measurement_sensor))
        except:
            self.run_in(self.initialize_when_ready,61)
            self.log("El. power Sensor not ready. Will try again later.")
            return
        self.log("El. Power Sensor ready. Value is {}".format(el_power))
        
        self.check_if_dryer_or_humidifier_needed()
        
        #dryer_or_humidifier already running?
        self.check_if_dryer_or_humidifier_running(None)
        
        self.check_if_dryer_or_humidifier_full_or_empty()

    def check_if_dryer_or_humidifier_needed(self):
        if self.machine_type == "dryer":
            if self.special_mode:
                if self.current_humidity >= (self.humidity_special_max - self.humidity_change_current):
                    self.turn_on(self.air_dryer_or_humidifier_switch)
                    self.run_in(self.check_if_dryer_or_humidifier_running,60)
                    self.dryer_or_humidifier_needed = True
    #                self.log("Special Mode, dryer_or_humidifier needed")
                elif self.current_humidity < (self.humidity_special_min - self.humidity_change_current):
                    self.turn_off(self.air_dryer_or_humidifier_switch)
                    self.dryer_or_humidifier_needed = False
    #                self.log("Special Mode, dryer_or_humidifier not needed")
                else:
                    self.dryer_or_humidifier_needed = False
    #                self.log("Special Mode, Humidity in target range, will do nothing")
            else:
                if self.current_humidity >= (self.humidity_standard_max - self.humidity_change_current):
                    self.turn_on(self.air_dryer_or_humidifier_switch)
                    self.run_in(self.check_if_dryer_or_humidifier_running,60)
                    self.dryer_or_humidifier_needed = True
    #                self.log("Standard Mode, dryer_or_humidifier needed")
                elif self.current_humidity < (self.humidity_standard_min - self.humidity_change_current):
                    self.turn_off(self.air_dryer_or_humidifier_switch)
                    self.dryer_or_humidifier_needed = False
    #                self.log("Standard Mode, dryer_or_humidifier not needed") 
                else:
                    self.dryer_or_humidifier_needed = False
    #                self.log("Standard Mode, Humidity in target range, will do nothing")
        elif self.machine_type == "humidifier":
            if self.special_mode:
                if self.current_humidity <= (self.humidity_special_min + self.humidity_change_current):
                    self.turn_on(self.air_dryer_or_humidifier_switch)
                    self.run_in(self.check_if_dryer_or_humidifier_running,60)
                    self.dryer_or_humidifier_needed = True
    #                self.log("Special Mode, dryer_or_humidifier needed")
                elif self.current_humidity > (self.humidity_special_max + self.humidity_change_current):
                    self.turn_off(self.air_dryer_or_humidifier_switch)
                    self.dryer_or_humidifier_needed = False
    #                self.log("Special Mode, dryer_or_humidifier not needed")
                else:
                    self.dryer_or_humidifier_needed = False
    #                self.log("Special Mode, Humidity in target range, will do nothing")
            else:
                if self.current_humidity <= (self.humidity_standard_min + self.humidity_change_current):
                    self.turn_on(self.air_dryer_or_humidifier_switch)
                    self.run_in(self.check_if_dryer_or_humidifier_running,60)
                    self.dryer_or_humidifier_needed = True
    #                self.log("Standard Mode, dryer_or_humidifier needed")
                elif self.current_humidity > (self.humidity_standard_max + self.humidity_change_current):
                    self.turn_off(self.air_dryer_or_humidifier_switch)
                    self.dryer_or_humidifier_needed = False
    #                self.log("Standard Mode, dryer_or_humidifier not needed") 
                else:
                    self.dryer_or_humidifier_needed = False
    #                self.log("Standard Mode, Humidity in target range, will do nothing")
        else:
            self.log("machine_type must be dryer or humidifier. Please check app config.")
    
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
                self.special_mode = True
            else:
                self.log("Es wurde wohl eine neue Zeit eingestellt. Werde neuen Timer setzen")
                if self.timer_handle != None:
                    self.cancel_timer(self.timer_handle)
                    self.log("Timer wurde abgebrochen")
                self.time_internal_state = round(float(new))
                self.timer_handle = self.run_in(self.stunde_abgelaufen,3600)
                self.special_mode = True
        self.check_if_dryer_or_humidifier_needed()

    def humidity_state_changed(self, entity, attributes, old, new, kwargs):
        self.current_humidity = float(self.get_state(self.humidity_sensor))
        self.check_if_dryer_or_humidifier_needed()
            
    def pv_power_changed(self, entity, attributes, old, new, kwargs):
        try: 
            value = float(new)
            if (-1 * value) > self.pv_power_for_step_1:
                self.humidity_change_current = self.humidity_change_step_1
            else:
                self.humidity_change_current = 0
        except:
            self.log("error converting new value to float")
            pass
        
    def electrical_measurement_state_changed(self, entity, attributes, old, new, kwargs):
        if float(new) > 1.0:
            self.dryer_or_humidifier_is_running = True
            self.set_state(self.name_reminder_switch_tank, state = "off", attributes = self.attributes_reminder_tank)
            #self.log("measurement changed, above 1, set reminder to off")
        else:
            self.dryer_or_humidifier_is_running = False
#            self.log("measurement changed, below 1, will check if dryer_or_humidifier full")
            self.check_if_dryer_or_humidifier_full_or_empty()
        
    def check_if_dryer_or_humidifier_running(self, kwargs):
        if float(self.get_state(self.energy_measurement_sensor)) > 1.0:
            self.dryer_or_humidifier_is_running = True
        else:
            self.dryer_or_humidifier_is_running = False
            self.check_if_dryer_or_humidifier_full_or_empty()
    
    def check_if_dryer_or_humidifier_full_or_empty(self):
        if self.dryer_or_humidifier_needed and not self.dryer_or_humidifier_is_running:
            self.log("Tank Luftdrockner ist wohl voll")
            self.set_state(self.name_reminder_switch_tank, state = "on", attributes = self.attributes_reminder_tank)
        else:
            self.set_state(self.name_reminder_switch_tank, state = "off", attributes = self.attributes_reminder_tank)
#            self.log("Tank ist wohl nicht voll. dryer_or_humidifier_needed ist {}, dryer_or_humidifier_is_running ist {}".format(self.dryer_or_humidifier_needed, self.dryer_or_humidifier_is_running))
        
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
