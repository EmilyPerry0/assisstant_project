from transcriber import Transcriber
from gemini import Gemini
from weatherHandler import get_weekly_weather

import logging

class Assisstant:
    def __init__(self):
        self.transcriber = Transcriber()
        self.gen_ai_model = Gemini()

        # set up logger
        self.log = logging.getLogger("assisstant")

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
                if 'weather' in transcribed_command:
                    self.log.debug('will use weather handling seprately')
                    weekly_weather = get_weekly_weather()['daily']
                    daily_weather = weekly_weather[0]
                    min_temp = daily_weather['temp']['min']
                    max_temp = daily_weather['temp']['max']
                    output_str = daily_weather['summary'] + " with a high of: " + str(max_temp) + " degrees and a low of: " + str(min_temp) + ' degrees.'
                    print(output_str)
                elif 'timer' in transcribed_command:
                    # TODO: Implement timer handling
                    self.log.debug('will use timer handling seprately')
                elif 'alarm' in transcribed_command:
                    # TODO Implement alarm handling
                    self.log.debug('will handle alarms seprately as well')
                else:
                    self.gen_ai_model.query_gemini(transcribed_command)
                    self.gen_ai_model.save_important_info(transcribed_command)
                wake_word_said = False

        except KeyboardInterrupt:
            pass # this feels like icky coding
        finally:
            self.transcriber.shutdown_protocol()
