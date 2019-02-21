import appdaemon.plugins.hass.hassapi as hass

#
# App to notify when arrived at work
#
# Args:
# zone = Name of zone (only name of zone)
# device = tracked device (fully qualified => device_tracker.device_name)
#

class notify_work_arrived(hass.Hass):

    def initialize(self):
        self.listen_state(self.arrived, self.args["device"], new = self.args["zone"])
        self.listen_state(self.left, self.args["device"], old = self.args["zone"])
        
    def arrived(self, entity, attribute, old, new, kwargs):
        self.log("Jo arrived at work")
        time_at_work = self.get_state("sensor.jo_at_work")
        self.log("Time at work: {}".format(time_at_work))
        if time_at_work == "0.0":
            self.fire_event("custom_notify", message="Angekommen", target="telegram_jo")
            #self.notify("Angekommen", name = "telegram_jo")

    def left(self, entity, attribute, old, new, kwargs):
        if new != self.args["zone"]:
            self.log("Jo left work")
            time_at_work_hm = self.get_state("sensor.jo_at_work", attribute="value")
            self.log("Time at work: {}".format(time_at_work_hm))
            self.fire_event("custom_notify", message="Feierabend! Reicht auch, nach {}".format(time_at_work_hm), target="telegram_jo")
