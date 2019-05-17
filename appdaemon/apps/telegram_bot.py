import appdaemon.plugins.hass.hassapi as hass
import datetime
import random

#
# Telegram Chatbot
# Args: a yaml list of conversations
# 

class telegram_bot(hass.Hass):

    def initialize(self):
        """Listen to Telegram Bot events of interest."""
        self.listen_event(self.receive_telegram_text, 'telegram_text')
        self.listen_event(self.receive_telegram_command, 'telegram_command')
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
        
        # Extract Keywords for Conversations
        conversations = self.args["conversations"]
        self.categories_threesteps = []
        self.categories_twosteps = []
        for category in conversations["threesteps"].keys():
            self.categories_threesteps.append(category)
        for category in conversations["twosteps"].keys():
            self.categories_twosteps.append(category)
        # Test: suche Räume für Licht
        #for room in conversations["threesteps"]["Licht"]["steps"].keys():
        #    self.log(room)
        # Test: suche Lichter im Wohnzimmer
        #for light in conversations["threesteps"]["Licht"]["steps"]["Wohnzimmer"].keys():
        #    self.log(light)
        # Test: suche Werte für Panels im Wohnzimmer, einzelne Werte
        #for value in conversations["threesteps"]["Licht"]["steps"]["Wohnzimmer"]["Panels"]["values"]:
        #    self.log(value)
        # Test: suche Werte für Panels im Wohnzimmer, als Liste
        #self.log(conversations["threesteps"]["Licht"]["steps"]["Wohnzimmer"]["Panels"]["values"])
        
        # Initialize Conversation Handler Variables
        self.conv_handler_curr_step = {}
        self.conv_handler_curr_type = {}
        for user_id in self.args["allowed_user_ids"]:
            self.conv_handler_curr_step.update( {user_id : 0} )
            self.conv_handler_curr_type.update( {user_id : 0} )
    
    def receive_telegram_text(self, event_id, payload_event, *args):
        assert event_id == 'telegram_text'
        chat_id = payload_event['chat_id']
        user_id = payload_event['user_id']
        text = payload_event['text']
        self.log(text)
        
        if self.conv_handler_curr_step[user_id] > 0:
            # Conversation Handler is waiting for an answer => pass the answer to it
            newstep = self.conv_handler_curr_step[user_id] + 1
            self.conv_handler_curr_step.update( {user_id : newstep} )
            self.conversation_handler(user_id, chat_id, text)
            
        else: # user is not in an active conversation
            
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
            if text in self.categories_threesteps:
                self.log("Keyword of 3 Step Conversation Found")
                self.conv_handler_curr_type.update( {user_id : 3} )
                self.conversation_handler(user_id, chat_id, text)
            
            # --- Konversation 2-Steps ---
            if text in self.categories_twosteps:
                self.log("Keyword of 2 Step Conversation Found")
                self.conv_handler_curr_type.update( {user_id : 2} )
                self.conversation_handler(user_id, chat_id, text)
            
            # --- Status Conversation ---
            if text.lower().startswith("status"):
                t = self.conv_handler_curr_type[user_id]
                s = self.conv_handler_curr_step[user_id]
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="Step: {}\nType: {}".format(s,t))
            
            # --- Reset Conversation ---
            if text.lower().startswith("reset"):
                self.conv_handler_curr_type.update( {user_id : 0} )
                self.conv_handler_curr_step.update( {user_id : 0} )
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="Conversation Reset")

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

    def conversation_handler(self, user_id, chat_id, text):
        self.log("Started Conversation")
