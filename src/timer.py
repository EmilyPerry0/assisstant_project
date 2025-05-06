import time
import threading
import logging
from pydub import AudioSegment
from pydub.playback import play

class Timer:
    def __init__(self, start_hours, start_minutes, start_seconds, assisstant):
        self.log = logging.getLogger("timer")
        self.stop_event = threading.Event()
        self.assisstant = assisstant
        self.start_hours = start_hours
        self.start_minutes = start_minutes
        self.start_seconds = start_seconds
        
        self.total_length_string = ""

        # create the string to verbalize the inital timer length
        if self.start_hours != "0":
            if self.start_hours == "1":
                self.total_length_string += "1 hour "
            else :
                self.total_length_string += self.start_hours + " hours "
        
        if self.start_minutes != "0":
            if self.start_minutes == "1":
                self.total_length_string += "1 minute "
            else:
                self.total_length_string += self.start_minutes + " minutes "
        
        if self.start_seconds != "0":
            if self.start_seconds == "1":
                self.total_length_string += "1 second"
            else:
                self.total_length_string += self.start_seconds + " seconds "
        
    def start(self, length):
        self.start_time = time.time()
        self.length = length
        self.thread = threading.Thread(target=self.check)
        self.thread.daemon = True
        self.thread.start()
        self.log.debug(f"Timer created for {self.length} seconds")
        
    def check(self):
        while not self.stop_event.is_set():
            curr_time = time.time()
            if curr_time-self.start_time >= self.length:
                self.log.debug('Timer ended')
                self.end()
                break
            time.sleep(1)
        return
            
    def time_left(self):
        curr_time = time.time()
        return int(self.length - (curr_time-self.start_time))
    
    def play_sound(self):
        alarm_sound = AudioSegment.from_file("assets/alarm.mp3")
        play(alarm_sound)
    
    def end(self):
        # Something happens here
        ## TODO Figure out how to have this method interrupt if necessary
        audioThread = threading.Thread(target=self.play_sound)
        audioThread.start()
        self.stop_event.set()
        audioThread.join()
        print(f"Your {self.total_length_string}timer has ended")
        self.assisstant.delete_timer(self.length)