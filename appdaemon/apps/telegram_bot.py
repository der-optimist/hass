import appdaemon.plugins.hass.hassapi as hass
import datetime
import random

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
        conversations = self.args["conversations"]
        #self.log(conversations)
        categories_threesteps = []
        categories_twosteps = []
        for category in conversations["threesteps"].keys():
            categories_threesteps.append(category)
        for category in conversations["twosteps"].keys():
            categories_twosteps.append(category)
        # Test: suche Räume für Licht
        for room in conversations["threesteps"]["Licht"]["steps"].keys():
            self.log(room)
    
    def receive_telegram_text(self, event_id, payload_event, *args):
        assert event_id == 'telegram_text'
        chat_id = payload_event['chat_id']
        text = payload_event['text']
        self.log(text)
        
        # --- Temperaturen ---
        if text.lower().startswith("temp"):
            self.send_temps(chat_id)
        
        # --- Wettervorhersage ---
        if text.lower().startswith("wetter") or text.lower().startswith("vorhersage"):
            self.send_weather_forecast(chat_id)
        
        # --- Danke Bitte ---
        if text.lower().startswith("danke"):
            self.answer_thank_you(chat_id)

        # --- Konversation 3-Steps ---
        if text in categories_threesteps:
            self.conversation_handler_threesteps(chat_id, text)

    def receive_telegram_command(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        command = payload_event['command']
        self.log(command)

    
    def receive_telegram_callback(self, event_id, payload_event, *args):
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']

    def send_temps(self, chat_id):
        temp_wz = self.get_state("sensor.t_wz_ist_oh")
        temp_aussen = self.get_state("sensor.temp_owm")
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="=== 🔥 Temperaturen ❄️ ===\nWohnzimmer: {} °C\nDraussen: {} °C".format(temp_wz,temp_aussen))
        
    def send_weather_forecast(self, chat_id):
        self.call_service('telegram_bot/send_photo',
                          target=chat_id,
                          file= "/config/www/meteograms/meteogram.png")
        
    def answer_thank_you(self, chat_id):
        reply = random.choice(["Gerne 😘", 
                           "Hey, du bist der Boss, ich mach nur was du sagst 😉", 
                           "Immer wieder gerne", 
                           "Bitteschön!"])
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=reply,
                          disable_notification=True)

    def conversation_handler_threesteps(self, chat_id, category):
        self.log("Started 3-Steps")
