import time
import threading
import logging
from pydub import AudioSegment
from pydub.playback import play

class Timer:
    def __init__(self):
        self.log = logging.getLogger("timer")
        self.stop_event = threading.Event()
        
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
        alarm_sound = AudioSegment.from_file("alarm.mp3")
        play(alarm_sound)
    
    def end(self):
        # Something happens here
        ## TODO Figure out how to have this method interrupt if necessary
        ## TODO Also figure out how to remove the timer from the Assistant object 'self.timer_dict'
        print("TIMER ENDED!!!!")
        audioThread = threading.Thread(target=self.play_sound)
        audioThread.start()
        self.stop_event.set()
        self.thread.join()