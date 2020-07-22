import appdaemon.plugins.hass.hassapi as hass

#
# make custom reminders survive a restart
#
# Args: 
# 

class save_reminders(hass.Hass):

    def initialize(self):
        # restore saved reminders after restart
        #self.restore_reminders(None)
       
        self.listen_state(self.update_saved_reminders, "switch")

    def update_saved_reminders(self, entity, attributes, old, new, kwargs):
        counter = 1
        for switch in self.get_state("switch"):
            if switch.startswith("switch.reminder_"):
                if self.get_state(switch) == "on":
                    friendly_name = self.get_state(switch, attribute="friendly_name")
                    icon = self.get_state(switch, attribute="entity_picture")
                    input_text_entity = "input_text.saved_reminder_0" + str(counter)
                    input_text_text = switch.split("switch.reminder_")[1] + "::" + friendly_name + "::" + icon
                    self.set_textvalue(input_text_entity, input_text_text)
                    counter = counter + 1
        for i in range(counter, 10):
            input_text_entity = "input_text.saved_reminder_0" + str(i)
            self.set_textvalue(input_text_entity, "empty")

    def restore_reminders(self, kwargs):
        for i in range(1, 10):
            input_text_entity = "input_text.saved_reminder_0" + str(i)
            text = self.get_state(input_text_entity)
            if text == "empty":
                self.log("{} ist leer".format(input_text_entity))
                continue
            if len(text.split("::")) == 3:
                switch_name = "switch.reminder_" + text.split("::")[0]
                friendly_name = text.split("::")[1]
                icon = text.split("::")[2]
                self.set_state(switch_name, state = "on", attributes={"entity_picture":icon, "friendly_name": friendly_name})
            else:
                self.log("input_text sollte 2 mal :: enthalten")
