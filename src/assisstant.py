from transcriber import Transcriber
from gemini import Gemini
from weatherHandler import get_weekly_weather
from timer import Timer
from alarm import Alarm
from classifier import detect_intent, detect_timer_sub_intent
import re

import string
import logging

class Assisstant:
    def __init__(self):
        self.transcriber = Transcriber()
        self.gen_ai_model = Gemini()

        # set up logger
        self.log = logging.getLogger("assisstant")
        
        # Create a dictionaries to store timers and alarms
        self.timer_dict = {}
        self.alarm_dict = {}


    def tokenize(self, command):
        # Take in a command and make it lowercase
        low_command = command.casefold()
        # Then remove punctuation
        text = re.sub(r"[-–—‑]", " ", low_command)
        command_stripped = re.sub(r"[^\w\s]", "", text)
        self.log.debug(command_stripped)
        # Turn that into a list split on all whitespace
        command_list = command_stripped.split()
        return command_list
    
    def words_to_int(self, s):
        # could maybe move these declarations to class member variables, but probably no need
        digits = ['0','1','2','3','4','5','6','7','8','9']
        units = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
            "eighteen": 18, "nineteen": 19
        }
        tens = {
            "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70,
            "eighty": 80, "ninety": 90
        }
        multiples = {
            "hundred": 100,
            "thousand": 1000,
            "million": 1000000,
        }
        # Normalize input
        s = s.casefold().replace('-', ' ').replace(' and ', ' ')
        tokens = s.split()

        result = 0
        current = 0
        flag = 0

        for token in tokens:
            if token in digits:
                current += int(token)
            elif token in units:
                current += units[token]
            elif token in tens:
                current += tens[token]
            elif token in multiples:
                current *= multiples[token]
                result += current
                current = 0
            elif token.isdigit(): # sometimes it just transcribes as a number (but in string datatype)
                result += int(token)
            else:
                self.log.debug(f"{s} is not a number")
                flag += 1
                
        if flag == len(tokens):
            return -1
        else:
            return result + current

    def handle_unkown_timers(self, mode):
        # No timers = literally free
        if len(self.timer_dict) == 0:
            print("There are no timers")
        # If there is only one timer: easy peasy
        elif len(self.timer_dict) == 1:
            if mode == 'l':
                # Get the only value stored in the dict and check its time
                time_left = list(self.timer_dict.values())[0].time_left()
                print(f"There are {time_left} seconds on your {list(self.timer_dict.keys())[0]} second timer.")
            elif mode =='r':
                ## TODO Figure out how to delete timers
                self.timer_dict
            else:
                self.log.debug(f"Unknown mode: {mode}")
        # If there are multiple timers: uh-oh
        else :
            timer_str = ""
            # Loop through all but the last key in the dictionary
            for item in list(self.timer_dict.keys())[:-1]:
                timer_str += str(item) + " seconds, "
            # Specifically do something different for the last item
            timer_str += " and " + str(list(self.timer_dict)[-1]) + " seconds."
            # List all of the timers and ask which one the user is referring to
            print("You have timers of length: " + timer_str + " Which timer are you like talking about?")
            
            # Get their answer and process it
            self.second_transcriber = Transcriber()
            answer = self.second_transcriber.transcribe_command()
            while answer == None:
                answer = self.second_transcriber.transcribe_command()
            answer_tokens = self.tokenize(answer)
            if answer_tokens[-1] == 'one':
                answer_tokens.pop()
            digi_list = []
            for item in answer_tokens:
                if self.words_to_int(item) != -1: # This should work I think????
                    digi_list.append(self.words_to_int(item)) # Collect all of the numbers that they may have said
            
            # If they don't say a number we can just go back to normal waiting mode
            if len(digi_list) == 0:
                print("Sorry, I didn't hear a number in that")
                return
            # If they only say one timer
            elif len(digi_list) == 1:
                for item in digi_list:
                    try:
                        curr_timer = self.timer_dict[item]
                    except KeyError:
                        print(f"You said the timer for {item} seconds. Thiere is not a timer set for this length womp womp.")
                        return
                    else:
                        length = item
                if mode == 'l':
                    print(f"There are {curr_timer.time_left()} seconds left in your {length} second timer.")
                elif mode == 'r':
                    ## TODO Figure out how to cancel a timer
                    print(f"Sure! Canceled your {length} minute timer")
                else:
                    self.log.debug(f"Unknown mode passed to handle_unknown_timers: {mode}")
            # If there they want to work with multiple timers >:(
            else:
                self.handle_multiple_timers(mode=mode, digi_list=digi_list)
                    
    def handle_multiple_timers(self, mode, digi_list):
        flag = 0
        timer_str2 = ""
        for item in digi_list[:-1]:
            try:
                curr_timer = self.timer_dict[item]
            except KeyError:
                self.log.debug(f"You said the timer for {item} seconds. Thiere is not a timer set for this length womp womp.")
                flag += 1
            else:
                if mode == 'l':
                    timer_str2 += f"You have {str(curr_timer.time_left())} seconds left on your {str(item)} second timer, "
                elif mode == 'r':
                    timer_str2 += f""
                else:
                    self.log.debug(f"Unkown mode: {mode}")
        # Special handling for the very last item
        try:
            curr_timer = self.timer_dict[digi_list[-1]]
        except KeyError:
            self.log.debug(f"You said the timer for {digi_list[-1]} seconds. Thiere is not a timer set for this length womp womp.")
            flag += 1
        else:
            if mode == 'l':
                timer_str2 += f"and you have {str(curr_timer.time_left())} seconds left on your {str(item)} second timer."
            elif mode == 'r':
                timer_str2 += ""
            else:
                self.log.debug(f"Unknown mode {mode}")
        if flag < len(digi_list):
            print("test " + timer_str2)
        else:
            print("None of the timers that you mentioned existed. What the literal fuck is wrong with you?")
    
    def delete_timer(self, timer_length):
        self.timer_dict.pop(timer_length)
        self.log.debug(f"number of timers remaining: {len(self.timer_dict)}")
                            
    def weather_handling(self, tokenized_command, transcribed_command):
        self.log.debug("weather handling running....")
        # Get a list of weather for the next week
        weekly_weather, today_hourly_data = get_weekly_weather()['daily']
        # If they mention tomorrow
        if 'tomorrow' in tokenized_command:
            daily_weather = weekly_weather[1]
        # Otherwise assume they mean today
        else:
            daily_weather = weekly_weather[0]
        # Get the min and max temps
        high = max(hour['temp'] for hour in today_hourly_data)
        low = min(hour['temp'] for hour in today_hourly_data)
        # Put it into a string that can be used by TTS
        output_str = daily_weather['summary'] + " with a high of: " + str(high) + " degrees and a low of: " + str(low) + ' degrees.'
        print(output_str)
    
    def timer_handling(self, tokenized_command, transcribed_command):
        self.log.debug('timer handling running...')
        # Look for words related to setting a timer
        timer_sub_intent = detect_timer_sub_intent(transcribed_command)
        
        if timer_sub_intent == 'create':
            self.log.debug('Here is where the timer is created')
            # Set some default vals
            hours = "0"
            mins = "0"
            seconds = "0"
            # Look for the specified time length
            for index in range(len(tokenized_command)):
                if (tokenized_command[index] == 'hours' or tokenized_command[index] == 'hour') and index != 0:
                    hours = tokenized_command[index-1]
                if (tokenized_command[index] == 'minutes' or tokenized_command[index] == 'minute') and index != 0:
                    mins = tokenized_command[index-1]
                if (tokenized_command[index] == 'seconds' or tokenized_command[index] == 'second') and index != 0:
                    seconds = tokenized_command[index-1]
            # Calculate the number of seconds
            self.log.debug(f"Hours: {hours}, Mins: {mins}, Seconds: {seconds}")
            timer_length = (self.words_to_int(seconds) + 60*(self.words_to_int(mins) + 60*self.words_to_int(hours)))
            timer = Timer(start_hours=hours, start_minutes=mins, start_seconds=seconds, assisstant=self)
            timer.start(length=timer_length)
            self.timer_dict[timer_length] = timer # Add it to a dictionary that tracks all of the timers by their set length
            self.log.debug(f"there are now {len(self.timer_dict)} timers")
        # If they ask how long is left
        elif timer_sub_intent == 'check':
            time_list = []
            for item in tokenized_command:
                if self.words_to_int(item) != -1:
                    time_list.append(self.words_to_int(item))
            if len(time_list) == 0:
                self.handle_unkown_timers(mode='l')
            elif len(time_list) == 1:
                    try:
                        curr_timer = self.timer_dict[time_list[0]]
                        length = time_list[0]
                    except KeyError:
                        self.log.debug(f"Timer of length {time_list[0]} not found")
                    else:
                        print(f"There are {curr_timer.time_left()} seconds left on your {length} second timer.")
            else:
                self.handle_multiple_timers(mode='l', digi_list=time_list)

            self.log.debug("Here it will print how much time is left")
        # Code to remove timers
        elif timer_sub_intent == 'delete':
            self.log.debug("timer canceler running... ")
            time_list = []
            for item in tokenized_command:
                if self.words_to_int(item) != -1:
                    time_list.append(self.words_to_int(item))
            if len(time_list) == 0:
                self.handle_unkown_timers(mode='r')
            elif len(time_list) == 1:
                    try:
                        curr_timer = self.timer_dict[time_list[0]]
                        length = time_list[0]
                    except KeyError:
                        self.log.debug(f"Timer of length {time_list[0]} not found")
                    else:
                        print(f"Deleting your {length} second timer.")
                        ## TODO Figure out how to delete timers
            else:
                self.handle_multiple_timers(mode='r', digi_list=time_list)
                
        elif timer_sub_intent == 'list':
            self.log.debug('running timer lister... ')
            num_timers = len(self.timer_dict)
            print(f"You have {num_timers} timers")
            if num_timers == 1:
                print(f'You have a timer for {list(self.timer_dict.keys())[0]} seconds,')
            elif num_timers == 2:
                print(f'You have a timer for {list(self.timer_dict.keys())[0]} seconds,')
                print(f"and, a timer for {list(self.timer_dict.keys())[-1]} seconds")
            elif num_timers > 2:
                print(f'You have a timer for {list(self.timer_dict.keys())[0]} seconds,')
                for i in list(self.timer_dict.keys()[1:-1]):
                    print(f"a timer for {i} seconds, ")
                print(f"and, a timer for {list(self.timer_dict.keys())[-1]} seconds")
            
        # Handle any other entries
        else:
            self.log.debug(f"Unknown timer command with entry: {transcribed_command}")

    def alarm_handling(self, tokenized_command, transcribed_command):
        self.log.debug("alarm handling running...")
        if 'set' in tokenized_command or 'create' in tokenized_command or 'make' in tokenized_command:
            alarm_time = Alarm.calculate_time(tokenized_command)
            alarm = Alarm()
            alarm.start(alarm_time)
            self.alarm_dict[alarm_time] = alarm
            
        elif "cancel" in tokenized_command or 'delete' in tokenized_command or 'remove' in tokenized_command or 'stop' in tokenized_command:
            for item in tokenized_command:
                if item.isdatetime(): # Not correct syntax ATM
                    try:
                        self.alarm_dict[item]
                    except ValueError:
                        self.log.debug(f"Alarm set for {item} not found")
        else:
            if len(self.alarm_dict) == 0:
                print("You do not currently have any alarms. Would you like to set one?")
                return
            elif len(self.alarm_dict) == 1:
                print(f"You have one alarm set for {list(self.alarm_dict_dict.keys())[0]}")
            else:
                alarm_string = ""
                for item in list(self.alarm_dict.keys())[:-1]:
                    alarm_string += item + " "
                alarm_string += " and " + list(self.alarm_dict.keys())[-1]
                print("You have alarms set for " + alarm_string)

    def run(self):
        """Main Program flow: 
                -Listen for wake word
                -Record spoken command
                -Query Gemini with the command
                -Save contextual info (if applicable)
                -Reset to top
        """
        wake_word_said = False

        try:
            while True:
                self.log.debug("Listening for wake word...")
                while not wake_word_said:
                    wake_word_said = self.transcriber.listen_for_wake_word()
                    Alarm.check_alarms(alarms_dict=self.alarm_dict, assisstant=self)
                transcribed_command = self.transcriber.transcribe_command()
                while transcribed_command == None:
                    transcribed_command = self.transcriber.transcribe_command()
                # TODO Implement tokenizer (while preserving whitespace)
                tokenized_command = self.tokenize(transcribed_command)
                
                
                intent = detect_intent(transcribed_command)

                if intent == 'weather':
                    self.weather_handling(tokenized_command, transcribed_command)
                elif intent == 'timer':
                    self.timer_handling(tokenized_command, transcribed_command)
                elif intent == 'alarm':
                    self.alarm_handling(tokenized_command, transcribed_command)
                else:
                    self.gen_ai_model.query_gemini(transcribed_command)
                    self.gen_ai_model.save_important_info(transcribed_command)

                wake_word_said = False

        except KeyboardInterrupt:
            self.log.debug("Keyboard interrupt recieved") # Less icky I hope <3
        finally:
            self.transcriber.shutdown_protocol()
