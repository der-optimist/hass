import appdaemon.plugins.hass.hassapi as hass

#
# Helper app for "Glastaster" without temp. sensor => Listen for events on a GA (0 and 1) and shift heating temperature up / down.
# Additionally, provide current and target temp as text for showing on the "Glastaster"
#
# Args:
#  - ga_binary => the GA the app will listen for. Programmed in the buttons of the GT
#  - climate_entity
#  - ga_text_current_temp
#  - ga_text_target_temp
#  - sensor_name_current_temp_text
#  - sensor_name_target_temp_text


class heating_helper(hass.Hass):

    def initialize(self):
        # listen for knx events => button pressed
        self.listen_event(self.shift_target_temp_up, event = "knx_event", address = self.args["ga_binary"], data = 1)
        self.listen_event(self.shift_target_temp_down, event = "knx_event", address = self.args["ga_binary"], data = 0)
        # initialize current temp text
        new = self.get_state(self.args["climate_entity"], attribute="current_temperature")
        try:
            new_text = "Ist: {} °C".format(round(float(new),1))
        except Exception as e:
            self.log("Could not convert current temp to float. Error was {}".format(e))
            new_text = "Ist: ?? °C"
        self.set_state(self.args["sensor_name_current_temp_text"], state = new_text)
        # initialize target temp text
        new = self.get_state(self.args["climate_entity"], attribute="temperature")
        try:
            new_text = "Soll: {} °C".format(round(float(new),1))
        except Exception as e:
            self.log("Could not convert target temp to float. Error was {}".format(e))
            new_text = "Soll: ?? °C"
        self.set_state(self.args["sensor_name_target_temp_text"], state = new_text)
        # update texts when temps changed
        self.listen_state(self.update_current_temp_text, self.args["climate_entity"], attribute = "current_temperature")
        self.listen_state(self.update_target_temp_text, self.args["climate_entity"], attribute = "temperature")
        
    def shift_target_temp_up(self,event_name,data,kwargs):
        current_target_temp = self.get_state(self.args["climate_entity"], attribute="temperature")
        new_target_temp = float(current_target_temp) + 0.5
        self.call_service(self, "climate/set_temperature", entity_id = self.args["climate_entity"], temperature = new_target_temp)
        
    def shift_target_temp_down(self,event_name,data,kwargs):
        current_target_temp = self.get_state(self.args["climate_entity"], attribute="temperature")
        new_target_temp = float(current_target_temp) - 0.5
        self.call_service(self, "climate/set_temperature", entity_id = self.args["climate_entity"], temperature = new_target_temp)
        
    def update_current_temp_text(self, entity, attribute, old, new, kwargs):
        try:
            new_text = "Ist: {} °C".format(round(float(new),1))
        except Exception as e:
            self.log("Could not convert current temp to float. Error was {}".format(e))
            new_text = "Ist: ?? °C"
        self.set_state(self.args["sensor_name_current_temp_text"], state = new_text)
        
    def update_target_temp_text(self, entity, attribute, old, new, kwargs):
        try:
            new_text = "Soll: {} °C".format(round(float(new),1))
        except Exception as e:
            self.log("Could not convert target temp to float. Error was {}".format(e))
            new_text = "Soll: ?? °C"
        self.set_state(self.args["sensor_name_target_temp_text"], state = new_text)
