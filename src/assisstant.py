from transcriber import Transcriber
from gemini import Gemini
from weatherHandler import get_weekly_weather
from timer import Timer

import string
import logging

class Assisstant:
    def __init__(self):
        self.transcriber = Transcriber()
        self.gen_ai_model = Gemini()

        # set up logger
        self.log = logging.getLogger("assisstant")
        
        # Create a dictionary to store timers
        self.timer_dict = {}

    def tokenize(self, command):
        # Take in a command and make it lowercase
        low_command = command.casefold()
        # Then remove punctuation
        command_stripped = low_command.translate(None, string.punctuation)
        # Turn that into a list split on all whitespace
        command_list = command_stripped.split()
        # Return it
        return command_list

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
                
                ## WEATHER HANDLING
                if 'weather' in tokenized_command:
                    self.log.debug('will use weather handling seprately')
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
                        continue
                    # Get the min and max temps
                    min_temp = daily_weather['temp']['min']
                    max_temp = daily_weather['temp']['max']
                    # Put it into a string that can be used by TTS
                    output_str = daily_weather['summary'] + " with a high of: " + str(max_temp) + " degrees and a low of: " + str(min_temp) + ' degrees.'
                    print(output_str)
                    
                ## TIMER HANDLING
                elif 'timer' in tokenized_command:
                    self.log.debug('will use timer handling seprately')
                    # Look for words related to setting a timer
                    if 'set' in tokenized_command or 'create' in tokenized_command or 'start' in tokenized_command:
                        self.log.debug('Here is where the timer is created')
                        # Set some default vals
                        hours = 0
                        mins = 0
                        seconds = 0
                        # Look for the specified time length
                        for index in range(len(tokenized_command)):
                            if (tokenized_command[index] == 'hours' or tokenized_command[index] == 'hour') and index != 0:
                                hours = tokenized_command[index-1]
                            if (tokenized_command[index] == 'minutes' or tokenized_command[index] == 'minute') and index != 0:
                                mins = tokenized_command[index-1]
                            if (tokenized_command[index] == 'seconds' or tokenized_command[index] == 'second') and index != 0:
                                seconds = tokenized_command[index-1]
                        # Calculate the number of seconds
                        timer_length = (seconds + 60*(mins + 60*hours))
                        timer = Timer() # Create the timer object
                        timer.start(length=timer_length) # Start the timer
                        self.timer_dict[timer_length] = timer # Add it to a dictionary that tracks all of the timers by their set length
                    # If they ask how long is left
                    elif 'left' in tokenized_command:
                        # If we have no timers say that
                        if len(self.timer_dict) == 0:
                            print("There are no timers")
                        # If there is only one timer say the time left
                        elif len(self.timer_dict) == 1:
                            time_left = self.timer_dict[0].check() # Don't think this is valid syntax ATM
                        # If there are multiple timers: uh-oh
                        else :
                            timer_str = ""
                            # Loop through all but the last key in the dictionary
                            for item in list(self.timer_dict)[:-1]:
                                timer_str += item + " seconds, "
                            # Specifically do something different for the last item
                            timer_str += " and " + list(self.timer_dict)[-1] + " seconds."
                            # List all of the timers and ask which one the user is referring to
                            print("You have timers of length: " + timer_str + " Which one would you like to ask about?")
                        self.log.debug("Here it will print how much time is left")
                    # Handle any other entried
                    else:
                        self.log.debug(f"Unknown timer command with entry: {transcribed_command}")
                        continue
                
                ## ALARM HANDLING
                elif 'alarm' in tokenized_command:
                    # TODO Implement alarm handling
                    self.log.debug('will handle alarms seprately as well')
                
                ## GEMINI HANDLING
                else:
                    self.gen_ai_model.query_gemini(transcribed_command)
                    self.gen_ai_model.save_important_info(transcribed_command)
                wake_word_said = False

        except KeyboardInterrupt:
            self.log.debug("Keyboard interrupt recieved") # Less icky I hope <3
            pass # this feels like icky coding
        finally:
            self.transcriber.shutdown_protocol()
