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
        """Text repeater."""
        assert event_id == 'telegram_text'
        user_id = payload_event['user_id']
        text = payload_event['text']
        self.log(text)


    def receive_telegram_command(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        command = payload_event['command']
        self.log(command)

    
    def receive_telegram_callback(self, event_id, payload_event, *args):
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']
