from datetime import datetime
import threading
import logging

class Alarm:
    def __init__(self):
        self.log = logging.getLogger("alarm")
        
    def start(self, time):
        self.end_time = time
        threading.Timer(1.0, self.check()).start()
        self.log(f"Alarm set for {self.end_time} O'clock.")
        
    def check(self):
        curr_time = datetime.now().replace(microsecond=0)
        if curr_time >= self.end_time:
            self.end()
    
    def end(self):
        ## TODO Implement ending things here
        pass