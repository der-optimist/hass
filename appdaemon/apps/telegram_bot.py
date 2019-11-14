import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
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
        self.conversations = self.args["conversations"]
        self.conversations = self.replace_secrets(self.conversations, self.convert)
        self.categories_threesteps = []
        self.categories_twosteps = []
        for category in self.conversations["threesteps"].keys():
            self.categories_threesteps.append(category)
        for category in self.conversations["twosteps"].keys():
            self.categories_twosteps.append(category)
        
        # Initialize Conversation Variables
        self.conv_handler_curr_type = {}
        self.conv_handler_curr_commands = {}
        for user_id in self.args["allowed_user_ids"]:
            self.reset_conversation_commands(user_id)
        
        self.call_service('telegram_bot/send_message',
                          target=self.args["allowed_user_ids"][0],
                          message="Nuc-Bot restarted 👍")
    
    def receive_telegram_text(self, event_id, payload_event, *args):
        assert event_id == 'telegram_text'
        chat_id = payload_event['chat_id']
        user_id = payload_event['user_id']
        text = payload_event['text']
        self.log(text)
        
        # --- check if user allowed
        if not user_id in self.args["allowed_user_ids"]:
            self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="⛔")
            return
        
        # --- Status Conversation ---
        if text.lower().startswith("status"):
            t = self.conv_handler_curr_type[user_id]
            c = self.conv_handler_curr_commands[user_id]
            self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="Commands: {}, {}, {}, {}\nType: {}".format(c[0],c[1],c[2],c[3],t))
        
        # --- Reset Conversation ---
        if text.lower().startswith("reset"):
            self.reset_conversation_commands(user_id)
            self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="Conversation Reset")
        
        if self.conv_handler_curr_type[user_id] == 2:
            # User is currently in a 2-Step conversation
            if self.conv_handler_curr_commands[user_id][1] == 0:
                # choice 1 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice1_twostep(user_id, chat_id, text)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            else:
                if self.conv_handler_curr_commands[user_id][2] == 0:
                    # choice 2 wurde wohl getroffen => Fuehe Befehl aus
                    commands = self.conv_handler_curr_commands[user_id]
                    commands[2] = text
                    self.conv_handler_curr_commands.update( {user_id : commands} )
                reply = self.run_command_from_conversation(user_id, chat_id)
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=reply.replace("_", "\_"))
            
        elif self.conv_handler_curr_type[user_id] == 3:
            # User is currently in a 3-Step conversation
            if self.conv_handler_curr_commands[user_id][1] == 0:
                # choice 1 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice1_threestep(user_id, chat_id, text)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            elif self.conv_handler_curr_commands[user_id][2] == 0:
                # choice 2 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice2_threestep(user_id, chat_id, text)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            else:
                if self.conv_handler_curr_commands[user_id][3] == 0:
                    # choice 3 wurde wohl getroffen => Fuehe Befehl aus
                    commands = self.conv_handler_curr_commands[user_id]
                    commands[3] = text
                    self.conv_handler_curr_commands.update( {user_id : commands} )
                reply = self.run_command_from_conversation(user_id, chat_id)
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=reply.replace("_", "\_"))
            
        else: # user is not in an active conversation
            
            # --- Hallo/Start ---
            if text.lower().startswith("hallo") or text.lower().startswith("start") or text.lower().startswith("was ") or text.lower().startswith("test"):
                self.say_hello(chat_id)
            
            # --- Temperaturen ---
            if text.lower().startswith("temp"):
                self.send_temps(chat_id)
        
            # --- Wettervorhersage ---
            if text.lower().startswith("wetter") or text.lower().startswith("vorhersage"):
                self.send_weather_forecast(chat_id)
            
            # --- Müll erledigt ---
            if text.lower().startswith("müll"):
                self.log("Müll ist erledigt")
                all_ha_switches = self.get_state("switch")
                for switch, value in all_ha_switches.items():
                    if switch.startswith("switch.reminder_garbage_"):
                        self.turn_off(switch)
                self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="OK, super 👍")

            # --- Danke Bitte ---
            if text.lower().startswith("danke"):
                self.answer_thank_you(chat_id)
            
            # --- Treppenlicht Nacht ---
            if text.lower().startswith("treppe"):
                self.treppenlicht(chat_id)

            # --- Konversation 3-Steps ---
            if text in self.categories_threesteps:
                self.log("Keyword of 3 Step Conversation Found")
                self.conv_handler_curr_type.update( {user_id : 3} )
                self.react_on_keyword_threestep(user_id, chat_id, text)
            
            # --- Konversation 2-Steps ---
            if text in self.categories_twosteps:
                self.log("Keyword of 2 Step Conversation Found")
                self.conv_handler_curr_type.update( {user_id : 2} )
                self.react_on_keyword_twostep(user_id, chat_id, text)
 

    def receive_telegram_command(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        chat_id = payload_event['chat_id']
        command = payload_event['command']
        self.log(command)
        
        # --- check if user allowed
        if not user_id in self.args["allowed_user_ids"]:
            self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="⛔")
            return

    
    def receive_telegram_callback(self, event_id, payload_event, *args):
        assert event_id == 'telegram_callback'
        user_id = payload_event['user_id']
        chat_id = payload_event['chat_id']
        data_callback = payload_event['data']
        callback_id = payload_event['id']
        
        # --- check if user allowed
        if not user_id in self.args["allowed_user_ids"]:
            self.call_service('telegram_bot/send_message',
                      target=chat_id,
                      message="⛔")
            return
        
        if self.conv_handler_curr_type[user_id] == 2:
            if self.conv_handler_curr_commands[user_id][1] == 0:
                # choice 1 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice1_twostep(user_id, chat_id, data_callback)
                self.call_service('telegram_bot/answer_callback_query',
                              message="",
                              callback_query_id=callback_id,
                              show_alert=False)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            else:
                if self.conv_handler_curr_commands[user_id][2] == 0:
                    # choice 2 wurde wohl getroffen => Fuehe Befehl aus
                    commands = self.conv_handler_curr_commands[user_id]
                    commands[2] = data_callback
                    self.conv_handler_curr_commands.update( {user_id : commands} )
                reply = self.run_command_from_conversation(user_id, chat_id)
                self.call_service('telegram_bot/answer_callback_query',
                              message="",
                              callback_query_id=callback_id,
                              show_alert=False)
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=reply.replace("_", "\_"))
                
        if self.conv_handler_curr_type[user_id] == 3:
            if self.conv_handler_curr_commands[user_id][1] == 0:
                # choice 1 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice1_threestep(user_id, chat_id, data_callback)
                self.call_service('telegram_bot/answer_callback_query',
                              message="",
                              callback_query_id=callback_id,
                              show_alert=False)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            elif self.conv_handler_curr_commands[user_id][2] == 0:
                # choice 2 wurde wohl getroffen => verarbeiten
                reply = self.react_on_choice2_threestep(user_id, chat_id, data_callback)
                self.call_service('telegram_bot/answer_callback_query',
                              message="",
                              callback_query_id=callback_id,
                              show_alert=False)
                self.call_service('telegram_bot/send_message',
                    target=chat_id,
                    message=reply["message"],
                    disable_notification=True, 
                    inline_keyboard=reply["keyboard"])
            else:
                if self.conv_handler_curr_commands[user_id][3] == 0:
                    # choice 3 wurde wohl getroffen => Fuehe Befehl aus
                    commands = self.conv_handler_curr_commands[user_id]
                    commands[3] = data_callback
                    self.conv_handler_curr_commands.update( {user_id : commands} )
                reply = self.run_command_from_conversation(user_id, chat_id)
                self.log(reply)
                self.call_service('telegram_bot/answer_callback_query',
                              message="",
                              callback_query_id=callback_id,
                              show_alert=False)
                self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=reply.replace("_", "\_"))
                

    def say_hello(self, chat_id):
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="Hallo! Ich kann dir bei ein paar Sachen behilflich sein, "\
                                  "z.B. kann ich dir das Licht an oder aus machen, Heizung einstellen, "\
                                  "Jalousien runter fahren oder auch einfach nur die aktuellen "\
                                  "Temperaturen oder die Wettervorschau schicken.\n"\
                                  "Schreibe mir einfach \"Licht\", \"Jalousie\", \"Heizung\", "\
                                  "\"Wetter\" oder \"Temperaturen\". Ohne die Anführungszeichen.\n"\
                                  "Wenn ich mehr wissen muss, dann frage ich schon.\n"\
                                  "Achso, mit \"Müll\" schalte ich übrigens die aktuelle Müll-Erinngerung aus.\n"\
                                  "So, jetzt aber viel Spaß 🙂\n"\
                                  "Achso, eins noch: toll siehst du aus 😉")

    def send_temps(self, chat_id):
        temp_ez = self.get_state("sensor.temp_esszimmer_taster")
        temp_aussen = self.get_state("sensor.temp_wetterstation")
        wind = self.get_state("sensor.windgeschwindigkeit_wetterstation_kmh")
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="=== 🔥 Temperaturen ❄️ ===\n"\
                                  "Esszimmer: {} °C\n"\
                                  "Draussen: {} °C\n"\
                                  "Wind: {} km/h".format(temp_ez,temp_aussen,wind))

    def treppenlicht(self, chat_id):
        self.turn_on("light.panels_treppe_og",brightness=self.pct_to_byte(5))
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message="Alles klar, gute Nacht an die Mädels...")

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
    
    def react_on_keyword_twostep(self, user_id, chat_id, text):
        self.log("2 Step Conversation started")
        # Stichwort für 2-Step-Konversation erkannt, lege text im Speicher ab und sende Möglichkeiten für 1. Auswahl
        commands = self.conv_handler_curr_commands[user_id]
        commands[0] = text
        self.conv_handler_curr_commands.update( {user_id : commands} )
        choices = []
        for key in self.conversations["twosteps"][commands[0]]["steps"].keys():
            choices.append(key)
        question = self.conversations["twosteps"][commands[0]]["q1"]
        reply = self.build_menu(choices, 3)
        self.call_service('telegram_bot/send_message',
                  target=chat_id,
                  message=question,
                  disable_notification=True, 
                  inline_keyboard=reply)
        
    def react_on_keyword_threestep(self, user_id, chat_id, text):
        self.log("3 Step Conversation started")
        # Stichwort für 3-Step-Konversation erkannt, lege text im Speicher ab und sende Möglichkeiten für 1. Auswahl
        commands = self.conv_handler_curr_commands[user_id]
        commands[0] = text
        self.conv_handler_curr_commands.update( {user_id : commands} )
        choices = []
        for key in self.conversations["threesteps"][commands[0]]["steps"].keys():
            choices.append(key)
        question = self.conversations["threesteps"][commands[0]]["q1"]
        reply = self.build_menu(choices, 3)
        self.call_service('telegram_bot/send_message',
                  target=chat_id,
                  message=question,
                  disable_notification=True, 
                  inline_keyboard=reply)
                      
    def react_on_choice1_twostep(self, user_id, chat_id, text):
        self.log("Processing choice 1 of 2")
        # 1. Auswahl von 2-Step-Konversation erkannt, lege text im Speicher ab und sende Möglichkeiten für 2. Auswahl
        commands = self.conv_handler_curr_commands[user_id]
        commands[1] = text
        self.conv_handler_curr_commands.update( {user_id : commands} )
        # check if there is a device for the given input
        try:
            device_name = self.conversations["twosteps"][commands[0]]["steps"][commands[1]]["device_name"]
        except KeyError as e:
            message = "Sorry - leider konnte ich zu {} kein passendes Gerät finden. Vielleicht vertippt?".format(commands[1])
            self.reset_conversation_commands(user_id)
            return {'message': message, 'keyboard': [[]] }
        # ok, there is a device, then there should be values
        choices = []
        for val in self.conversations["twosteps"][commands[0]]["steps"][commands[1]]["values"]:
            choices.append(val)
        keyboard = self.build_menu(choices, 4)
        message = self.conversations["twosteps"][commands[0]]["q2"]
        return {'message': message, 'keyboard': keyboard }
    
    def react_on_choice1_threestep(self, user_id, chat_id, text):
        self.log("Processing choice 1 of 3")
        # 1. Auswahl von 2-Step-Konversation erkannt, lege text im Speicher ab und sende Möglichkeiten für 2. Auswahl
        commands = self.conv_handler_curr_commands[user_id]
        commands[1] = text
        self.conv_handler_curr_commands.update( {user_id : commands} )
        # check if there is a device for the given input
        if not text in self.conversations["threesteps"][commands[0]]["steps"].keys():
            message = "Sorry - leider konnte ich zu {} kein passendes Gerät finden. Vielleicht vertippt?".format(commands[1])
            self.reset_conversation_commands(user_id)
            return {'message': message, 'keyboard': [[]] }
        choices = []
        for key in self.conversations["threesteps"][commands[0]]["steps"][commands[1]].keys():
            choices.append(key)
        keyboard = self.build_menu(choices, 3)
        message = self.conversations["threesteps"][commands[0]]["q2"]
        return {'message': message, 'keyboard': keyboard }
    
    def react_on_choice2_threestep(self, user_id, chat_id, text):
        self.log("Processing choice 2 of 3")
        # 2. Auswahl von 3-Step-Konversation erkannt, lege text im Speicher ab und sende Möglichkeiten für 3. Auswahl
        commands = self.conv_handler_curr_commands[user_id]
        commands[2] = text
        self.conv_handler_curr_commands.update( {user_id : commands} )
        # check if there is a device for the given input
        try:
            device_name = self.conversations["threesteps"][commands[0]]["steps"][commands[1]][commands[2]]["device_name"]
        except KeyError as e:
            message = "Sorry - leider konnte ich zu {}, {} kein passendes Gerät finden. Vielleicht vertippt?".format(commands[1], commands[2])
            self.reset_conversation_commands(user_id)
            return {'message': message, 'keyboard': [[]] }
        # ok, there is a device, then there should be values
        choices = []
        for val in self.conversations["threesteps"][commands[0]]["steps"][commands[1]][commands[2]]["values"]:
            choices.append(val)
        keyboard = self.build_menu(choices, 4)
        message = self.conversations["threesteps"][commands[0]]["q3"]
        return {'message': message, 'keyboard': keyboard }
    
    def run_command_from_conversation(self, user_id, chat_id):
        self.log("fire the command!")
        commands = self.conv_handler_curr_commands[user_id]
        if self.conv_handler_curr_type[user_id] == 2:
            value = commands[2]
            try:
                device_name = self.conversations["twosteps"][commands[0]]["steps"][commands[1]]["device_name"]
            except KeyError as e:
                reply = "Sorry - leider konnte ich zu {} kein passendes Gerät finden. Vielleicht vertippt?".format(commands[1])
                self.reset_conversation_commands(user_id)
                return reply
            device_type = self.conversations["twosteps"][commands[0]]["steps"][commands[1]]["device_type"]
        if self.conv_handler_curr_type[user_id] == 3:
            value = commands[3]
            try:
                device_name = self.conversations["threesteps"][commands[0]]["steps"][commands[1]][commands[2]]["device_name"]
            except KeyError as e:
                reply = "Sorry - leider konnte ich zu {}, {} kein passendes Gerät finden. Vielleicht vertippt?".format(commands[1], commands[1])
                self.reset_conversation_commands(user_id)
                return reply
            device_type = self.conversations["threesteps"][commands[0]]["steps"][commands[1]][commands[2]]["device_type"]
        # Please insert real action command...
        if device_type == "light_dim":
            if value == "Aus" or value == "aus":
                value = 0
            if value == "An" or value == "an":
                value = 100
            err = False
            try: 
                value_numeric = float(self.clean_command(value))
            except:
                reply = "Sorry, aber ich brauche entweder eine Zahl oder An oder Aus. So geht das nicht"
                err = True
            if not err:
                if value_numeric == float(0):
                    self.turn_off(device_name)
                    reply = "OK, habe {} ausgeschalten.".format(commands[2])
                else:
                    self.turn_on(device_name,brightness=self.pct_to_byte(value_numeric))
                    reply = "OK, habe {} auf Helligkeit {}% gestellt.".format(commands[2],value_numeric)
        if device_type == "light_switch":
            if value == "Aus" or value == "aus":
                self.turn_off(device_name)
                reply = "OK, habe {} ausgeschalten.".format(commands[2])
            elif value == "An" or value == "an":
                self.turn_on(device_name)
                reply = "OK, habe {} eingeschalten.".format(commands[2])
            else:
                reply = "Sorry, ich fresse An und Aus, alles andere wird wieder ausgespuckt..."
        if device_type == "jal":
            if value == "Auf" or value == "auf":
                value = 0
            if value == "Zu" or value == "zu":
                value = 100
            if value == "Blöde Frage" or value == "blöde Frage":
                value = 0
            err = False
            try: 
                value_numeric = float(self.clean_command(value))
            except:
                reply = "Sorry, aber ich brauche als Winkel entweder eine Zahl oder auf oder zu. So geht das nicht"
                err = True
            if not err:
                if commands[2] == "Runter" or commands[2] == "runter":
                    value_position_numeric = 100
                elif commands[2] == "Hoch" or commands[2] == "hoch":
                    value_position_numeric = 0
                else:
                    try: 
                        value_position_numeric = float(self.clean_command(commands[2]))
                    except:
                        reply = "Sorry, aber ich brauche als Position entweder eine Zahl oder hoch oder runter. So geht das nicht"
                        err = True
            if not err:
                self.call_service("cover/set_cover_position", entity_id = device_name, position = value_position_numeric)
                self.call_service("cover/set_cover_tilt_position", entity_id = device_name, tilt_position = value_numeric)
                reply = "OK, fahre die Jalousie {} {}% runter und drehe sie {}% zu.".format(commands[1],value_position_numeric,value_numeric)
        if device_type == "heat":
            err = False
            try: 
                value_numeric = float(self.clean_command(value))
            except:
                reply = "Sorry, aber ich brauche entweder eine Zahl. So geht das nicht"
                err = True
            if not err:
                if value_numeric > float(26):
                    reply = "Das ist aber ganz schön heiß, das traue ich mich nicht..."
                    err = True
                if value_numeric < float(16):
                    reply = "Das ist aber ganz schön kalt, das traue ich mich nicht..."
                    err = True
            if not err:
                self.call_service("climate/set_temperature", entity_id = device_name, temperature = value_numeric)
                reply = "OK, habe die Heizung {} auf {} °C gestellt.".format(commands[1],value_numeric)
        self.reset_conversation_commands(user_id)
        return reply
    
    def clean_command(self, command):
        if isinstance(command, str):
            command_clean = command.replace(" %", "").replace("%", "")
            command_clean = command_clean.replace(" °C", "").replace("°C", "").replace(" °", "").replace("°", "")
        else:
            command_clean = command
        return command_clean
    
    def reset_conversation_commands(self, user_id):
        self.conv_handler_curr_commands.update( {user_id : [0, 0, 0, 0]} )
        self.conv_handler_curr_type.update( {user_id : 0} )
        self.log("Commands reset for user {}".format(user_id))
        
    def build_menu(self, values, n_cols):
        while (len(values) % n_cols) > 0:
            values.append(" ")
        button_list = []
        counter = 0
        for row in range(len(values) // n_cols):
            list_row = []
            for column in range(n_cols):
                button = (values[counter], values[counter])
                counter = counter + 1
                list_row.append(button)
            button_list.append(list_row)
        return button_list
    
    def replace_secrets(self, obj, convert):
        """
        Recursively goes through the dictionary obj and replaces keys with the convert function.
        """
        if isinstance(obj, (str, int, float)):
            return obj
        if isinstance(obj, dict):
            new = obj.__class__()
            for k, v in obj.items():
                new[self.convert(k)] = self.replace_secrets(v, self.convert)
        elif isinstance(obj, (list, set, tuple)):
            new = obj.__class__(self.replace_secrets(v, self.convert) for v in obj)
        else:
            return obj
        return new

    def convert(self, text):
        for secret in self.args["secrets"].keys():
            text = text.replace(secret, self.args["secrets"][secret])
        return text

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
