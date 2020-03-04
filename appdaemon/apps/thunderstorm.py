import appdaemon.plugins.hass.hassapi as hass

#
# react on "thunderstorm" button
#
# Args:


class thunderstorm(hass.Hass):

    def initialize(self):
        pass
#        self.listen_state(self.gewitter_an, "input_boolean.gewitter", old = "off", new = "on")
#        self.listen_state(self.gewitter_aus, "input_boolean.gewitter", old = "on", new = "off")

    def gewitter_an(self, entity, attributes, old, new, kwargs):
        self.log("Gewitter!")
        message = "Gewitter! Ich nehme TV, Mixi, Lüftung, Waschmaschine und Trockner jetzt den Strom"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
        self.fire_event("custom_notify", message=message, target="telegram_ma")
        # TV
        self.turn_off("switch.tv")
        # Mixi
        self.turn_off("switch.mixi")
        # Lüftungsanlage
        self.turn_off("switch.luftungsanlage")
        # Waschmaschine
        if float(self.get_state("sensor.el_leistung_waschmaschine")) > 12:
            message = "Waschmaschine ist wohl grad an. Die lasse ich an"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
        else:
            self.turn_off("switch.waschmaschine")
        # Trockner
        if float(self.get_state("sensor.el_leistung_trockner")) > 4:
            message = "Trockner läuft wohl gerade. Den lasse ich an"
            self.fire_event("custom_notify", message=message, target="telegram_jo")
            self.fire_event("custom_notify", message=message, target="telegram_ma")
        else:
            self.turn_off("switch.trockner")

    def gewitter_aus(self, entity, attributes, old, new, kwargs):
        self.log("Gewitter ist wohl vorbei, gut")
        message = "Gewitter ist wohl vorbei, gut. Ich geb TV, Mixi, Lüftung, Waschmaschine und Trockner jetzt wieder Strom"
        self.fire_event("custom_notify", message=message, target="telegram_jo")
        self.fire_event("custom_notify", message=message, target="telegram_ma")
        self.turn_on("switch.tv")
        self.turn_on("switch.mixi")
        self.turn_on("switch.luftungsanlage")
        self.turn_on("switch.waschmaschine")
        self.turn_on("switch.trockner")
