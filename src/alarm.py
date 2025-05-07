from datetime import datetime
from datetime import timedelta
import time
import threading
import logging
from pydub import AudioSegment
from pydub.playback import play

class Alarm:
    def __init__(self):
        self.log = logging.getLogger("alarm")
        self.stop_event = threading.Event()
        
    def start(self, time):
        self.end_time = time
        self.thread = threading.Thread(target=self.check)
        self.thread.daemon = True
        self.thread.start()
        print(f"Alarm set for {self.end_time.time()} O'clock.")
        
    @staticmethod
    def check_alarms(alarms_dict, assisstant):
        for alarm_key in alarms_dict:
            if alarm_key.time() == datetime.now().time() and alarm_key.date() == datetime.now().date():
                alarms_dict[alarm_key].end()
                assisstant.delete_alarm(alarm_key)

    @staticmethod
    def normalize_time_string(time_string):
        result = str(time_string)
        if len(time_string) == 1 or len(time_string) == 2: # for if they said "1" or "12"
            result += "00"
        if ':' not in time_string:
            result = result[:-2] + ':' + result[-2:]
        return result

    
    # returns the datum of the alarm
    @staticmethod
    def calculate_time(tokenized_command):
        command_time = ""
        for index in range(len(tokenized_command)):
            if tokenized_command[index] == 'at' or tokenized_command[index] == 'for':
                command_time = tokenized_command[index+1]

        normalized_time = Alarm.normalize_time_string(command_time)
        parsed_time = datetime.strptime(normalized_time, "%H:%M")

        if (parsed_time.time() <= datetime.now().time() or "tomorrow" in tokenized_command) and "today" not in tokenized_command:
            target_date = datetime.now().date() + timedelta(days=1)
        else:
            target_date = datetime.now().date()
        result = datetime.combine(target_date, parsed_time.time())
        return result
        

    def check(self):
        while not self.stop_event.is_set():
            curr_time = datetime.now().replace(microsecond=0)
            if curr_time >= self.end_time:
                self.log.debug('Alarm ended')
                self.end()
                break
            time.sleep(1)
        return
    
    def play_sound(self):
        alarm_sound = AudioSegment.from_file("assets/alarm.mp3")
        play(alarm_sound)
    
    def end(self):
        ## TODO Implement ending things here
        audioThread = threading.Thread(target=self.play_sound)
        audioThread.start()
        self.stop_event.set()
        audioThread.join()

# dunno what this does but it executes when the program boots up
# Alarm.calculate_time(0,0,0,0,0,0)