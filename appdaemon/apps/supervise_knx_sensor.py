import appdaemon.plugins.hass.hassapi as hass

#
# App to check if a knx sensor send frequently. Otherwise, notify
#
# Args:
#  - ga (knx group address)
#  - sensor_name (only for Notification)
#  - minutes

class supervise_knx_sensor(hass.Hass):

    def initialize(self):
        self.timer_handle = self.run_in(self.notify_me,60*self.args["minutes"])
        self.listen_event(self.received_sensor_value, event = "knx_event", address = self.args["ga"])
    
    def received_sensor_value(self,event_name,data,kwargs):
        if self.timer_handle != None:
            self.cancel_timer(self.timer_handle)
        self.timer_handle = self.run_in(self.notify_me,60*self.args["minutes"])

    def notify_me(self, kwargs):
        self.log("Send warning, sensor did not send")
        self.fire_event("custom_notify", message="⚠️ KNX-Sensor {} hat nicht innerhalb {} Minuten gesendet ⚠️".format(self.args["sensor_name"],self.args["minutes"]), target="telegram_jo")
        self.timer_handle = None
