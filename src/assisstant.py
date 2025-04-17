from transcriber import Transcriber
from gemini import Gemini
from weatherHandler import get_weekly_weather
from timer import Timer
from alarm import Alarm

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

        # setup for tokenization
        self.punctuation_removal_table = str.maketrans("", "", string.punctuation)

    def tokenize(self, command):
        # Take in a command and make it lowercase
        low_command = command.casefold()
        # Then remove punctuation
        command_stripped = low_command.translate(self.punctuation_removal_table)
        # Turn that into a list split on all whitespace
        command_list = command_stripped.split()
        return command_list
    
    def words_to_int(self, s):
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
            else:
                self.log.debug(f"Unknown work entered {s}")
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
                timer_str += item + " seconds, "
            # Specifically do something different for the last item
            timer_str += " and " + list(self.timer_dict)[-1] + " seconds."
            # List all of the timers and ask which one the user is referring to
            print("You have timers of length: " + timer_str + " Which timer are you like talking about?")
            
            # Get their answer and process it
            answer = Transcriber.transcribe_command()
            answer_tokens = self.tokenize(answer)
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
                    print(timer_str2)
                else:
                    print("None of the timers that you mentioned existed. What the literal fuck is wrong with you?")
                            
    def weather_handling(self, tokenized_command, transcribed_command):
        self.log.debug("weather handling running....")
        # Get a list of weather for the next week
        weekly_weather = get_weekly_weather()['daily']
        # If they mention today get the appropriate day
        if 'today' in tokenized_command:
            daily_weather = weekly_weather[0]
        # If they mention tomorrow do the same
        elif 'tomorrow' in tokenized_command:
            daily_weather = weekly_weather[1]
        # Handle any other entries
        else:
            self.log.debug(f"Unknown weather command with entry: {transcribed_command}")
            self.log.debug(f"tokenized command: {tokenized_command}")
            return
        # Get the min and max temps
        min_temp = daily_weather['temp']['min']
        max_temp = daily_weather['temp']['max']
        # Put it into a string that can be used by TTS
        output_str = daily_weather['summary'] + " with a high of: " + str(max_temp) + " degrees and a low of: " + str(min_temp) + ' degrees.'
        print(output_str)
    
    def timer_handling(self, tokenized_command, transcribed_command):
        self.log.debug('timer handling running...')
        # Look for words related to setting a timer
        if 'set' in tokenized_command or 'create' in tokenized_command or 'start' in tokenized_command or 'add' in tokenized_command or 'make' in tokenized_command:
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
            timer = Timer()
            timer.start(length=timer_length)
            self.timer_dict[timer_length] = timer # Add it to a dictionary that tracks all of the timers by their set length
            
        # If they ask how long is left
        elif 'left' in tokenized_command or 'remaining' in tokenized_command:
            time_said = False
            for item in tokenized_command:
                if self.words_to_int(item) != 0:
                    time_said = True
                    try:
                        curr_timer = self.timer_dict[item]
                        length = item
                    except KeyError:
                        self.log.debug(f"Timer of length {item} not found")
                        time_said=False
            if not time_said:
                self.handle_unkown_timers(mode='l')
            else:
                print(f"There are {curr_timer.time_left()} seconds left on your {length} second timer.")
            # If we have no timers say that

            self.log.debug("Here it will print how much time is left")
        # Code to remove timers
        elif 'cancel' in tokenized_command or 'delete' in tokenized_command or 'remove' in tokenized_command or 'stop' in tokenized_command:
            time_said = False
            for item in tokenized_command:
                if self.words_to_int(item) != 0:
                    time_said = True
                    try:
                        self.timer_dict[item]
                    except KeyError:
                        self.log.debug(f"Timer of length {item} not found")
            if not time_said:
                self.handle_unkown_timers(mode='r')
            
        # Handle any other entries
        else:
            self.log.debug(f"Unknown timer command with entry: {transcribed_command}")

    def alarm_handling(self, tokenized_command, transcribed_commans):
        self.log.debug("alarm handling running...")
        if 'set' in tokenized_command or 'create' in tokenized_command or 'make' in tokenized_command:
            mins = "0"
            hour = "0"
            day_offset = "0"
            month_offset = "0"
            year_offset = "0"
            Alarm.calculate_time(mins,hour, day_offset, month_offset, year_offset)
            pass
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
                transcribed_command = self.transcriber.transcribe_command()
                # TODO Implement tokenizer (while preserving whitespace)
                tokenized_command = self.tokenize(transcribed_command)
                
                if 'weather' in tokenized_command:
                    self.weather_handling(tokenized_command, transcribed_command)
                elif 'timer' in tokenized_command or 'timers' in tokenized_command:
                     self.timer_handling(tokenized_command, transcribed_command)
                elif 'alarm' in tokenized_command:
                    # TODO Implement alarm handling
                    self.log.debug('will handle alarms seprately as well')                   
                else: # GEMINI HANDLING
                    self.gen_ai_model.query_gemini(transcribed_command)
                    self.gen_ai_model.save_important_info(transcribed_command)
                wake_word_said = False

        except KeyboardInterrupt:
            self.log.debug("Keyboard interrupt recieved") # Less icky I hope <3
        finally:
            self.transcriber.shutdown_protocol()
