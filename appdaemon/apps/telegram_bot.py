import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Telegram Chatbot
# Args: a yaml list of things and possible values
# 

class telegram_bot(hass.Hass):

    def initialize(self):
        """Listen to Telegram Bot events of interest."""
        self.listen_event(self.receive_telegram_text, 'telegram_text')
        self.listen_event(self.receive_telegram_command, 'telegram_command')
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
    
    def receive_telegram_text(self, event_id, payload_event, *args):
        assert event_id == 'telegram_text'
        chat_id = payload_event['chat_id']
        text = payload_event['text']
        self.log(text)
        
        if text.startswith("Temp"):
            self.send_temps(chat_id)


    def receive_telegram_command(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        command = payload_event['command']
        self.log(command)

    
    def receive_telegram_callback(self, event_id, payload_event, *args):
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']

    def send_temps(self, chat_id, kwargs):
        temp_wz = self.get_state("sensor.t_wz_ist_oh")
        temp_aussen = self.get_state("sensor.temp_owm")
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="1=== 🔥 Temperaturen ❄️ ===\nWohnzimmer: {} °C\nDraussen: {} °C".format(temp_wz,temp_aussen),
                          disable_notification=True)
        #self.fire_event("custom_notify", message="=== 🔥 Temperaturen ❄️ ===\nWohnzimmer: {} °C\nDraussen: {} °C".format(temp_wz,temp_aussen), target="telegram_jo")
