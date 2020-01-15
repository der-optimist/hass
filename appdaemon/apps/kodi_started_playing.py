import appdaemon.plugins.hass.hassapi as hass

#
# App sets an input_boolean to "on" when kodi starts playing
# and resets it to "off" a few seconds later 
# => switching off lights with auto-light app
# But: only in the evening!
#
# Args:
#

class kodi_started_playing(hass.Hass):

    def initialize(self):
        self.bool_var = "input_boolean.kodi_just_started_playing"
        self.active_time_entity = "binary_sensor.tv_zeit_abend"
        self.listen_state(self.kodi_state_changed, "media_player.kodi")
    
    def kodi_state_changed(self, entity, attribute, old, new, kwargs):
        if new == "playing" and old != new:
            if self.get_state(self.active_time_entity) == "on":
                self.turn_on(self.bool_var)
                self.run_in(self.reset_bool_var,2)
                self.log("Kodi started playing, we are in active time, did set Variable to on")
            else:
                self.log("Kodi started playing, but we are not in active time")
    
    def reset_bool_var(self, kwargs):
        self.turn_off(self.bool_var)
