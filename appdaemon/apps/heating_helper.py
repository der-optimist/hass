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

class heating_helper(hass.Hass):

    def initialize(self):
        self.listen_event(self.shift_target_temp_up, event = "knx_event", address = self.args["ga_binary"], data = 1)
        self.list_waiting_messages = []
        
    def shift_target_temp_up(self,event_name,data,kwargs):
        
