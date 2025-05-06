from datetime import datetime
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
        self.log(f"Alarm set for {self.end_time} O'clock.")
        
    def calculate_time(self, mins, hours, day_offset, month_offset, year_offset):
        time = datetime.now().time().replace(microsecond=0, second=0)
        day = datetime.now().day
        print(day)
        if time.hour < hours:
            day_offset += 1
        return
        
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
        alarm_sound = AudioSegment.from_file("alarm.mp3")
        play(alarm_sound)
    
    def end(self):
        ## TODO Implement ending things here
        print("TIMER ENDED!!")
        audioThread = threading.Thread(target=self.play_sound)
        audioThread.start()
        self.stop_event.set()
        self.thread.join()

# dunno what this does but it executes when the program boots up
# Alarm.calculate_time(0,0,0,0,0,0)