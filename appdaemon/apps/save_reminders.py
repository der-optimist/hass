import appdaemon.plugins.hass.hassapi as hass

#
# make custom reminders survive a restart
#
# Args: 
# 

class save_reminders(hass.Hass):

    def initialize(self):
        # restore saved reminders after restart
        self.restore_reminders(None)
       
        self.listen_state(self.update_saved_reminders, "switch")

    def update_saved_reminders(self, entity, attributes, old, new, kwargs):
        self.log("saving reminders")
        counter = 1
        for switch in self.get_state("switch"):
            if switch.startswith("switch.reminder_"):
                if self.get_state(switch) == "on":
                    if counter == 10:
                        self.log("Mehr als 9 Reminder sind fuer restore nicht vorgesehen, kann Reminder {} nicht speichern".format(switch))
                        continue
                    try:
                        friendly_name = self.get_state(switch, attribute="friendly_name")
                        icon = self.get_state(switch, attribute="entity_picture")
                        input_text_entity = "input_text.saved_reminder_0" + str(counter)
                        input_text_text = switch.split("switch.reminder_")[1] + "::" + friendly_name + "::" + icon
                        self.set_textvalue(input_text_entity, input_text_text)
                        counter = counter + 1
                    except Exception as e:
                        self.log("Error saving reminder {}. Error was: {}".format(switch,e))
        for i in range(counter, 10):
            input_text_entity = "input_text.saved_reminder_0" + str(i)
            self.set_textvalue(input_text_entity, "empty")

    def restore_reminders(self, kwargs):
        self.log("Will restore reminders")
        for i in range(1, 10):
            input_text_entity = "input_text.saved_reminder_0" + str(i)
            text = self.get_state(input_text_entity)
            if text == "empty":
                continue
            if len(text.split("::")) == 3:
                try:
                    switch_name = "switch.reminder_" + text.split("::")[0]
                    friendly_name = text.split("::")[1]
                    icon = text.split("::")[2]
                    self.set_state(switch_name, state = "on", attributes={"entity_picture":icon, "friendly_name": friendly_name})
                    self.log("restored reminder {} with text: {}".format(switch_name, friendly_name))
                except Exception as e:
                    self.log("Error saving reminder {}. Error was: {}".format(input_text_entity,e))
            else:
                self.log("input_text sollte 2 mal :: enthalten")
