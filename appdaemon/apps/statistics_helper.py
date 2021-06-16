import appdaemon.plugins.hass.hassapi as hass

#
# What it does: calculate mean or max values from a sensor over time
#   - 
# What args it needs:
#   - 
#  

class statistics_helper(hass.Hass):

    def initialize(self):
        self.input_entity = self.args["input_entity"]
        self.output_entity = self.args["output_entity"]
        self.number_of_values = self.args["number_of_values"]
        self.time_interval_sec = self.args["time_interval_sec"]
        self.function_type = self.args["function_type"] # min, max or mean
        self.trigger_type = self.args["trigger_type"] # currently only "fixed_timestep" supported
        self.list_of_values = []
        if self.trigger_type == "fixed_timestep":
            self.run_every(self.update_value_fixed_ts, "now+10", self.time_interval_sec)
        
    
    def update_value_fixed_ts(self, kwargs):
        sensor_state = self.get_state(self.input_entity, attribute="all")
        current_value_str = sensor_state["state"]
        if current_value_str.isnumeric():
            current_value = float(current_value_str)
            if len(self.list_of_values) < self.number_of_values:
                self.list_of_values = [current_value] + self.list_of_values
            else:
                self.list_of_values = [current_value] + self.list_of_values[0:self.number_of_values]
            if self.function_type == "mean":
                output_value = sum(self.list_of_values) / len(self.list_of_values)
            elif self.function_type == "max":
                output_value = max(self.list_of_values)
            elif self.function_type == "min":
                output_value = min(self.list_of_values)
            else:
                self.log("unknown function type")
            
            self.set_state(self.output_entity, state = output_value, attributes = sensor_state["attributes"])
