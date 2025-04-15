import time
import threading
import logging

class Timer:
    def __init__(self):
        self.log = logging.getLogger("timer")
        
    def start(self, length):
        self.start_time = time.time()
        self.length = length()
        threading.Timer(1, self.check()).start()
        
    def check(self):
        curr_time = time.time()
        if curr_time-self.start_time >= self.length:
            self.log.debug('Timer ended')
            self.end()
    
    def end(self):
        # Something happens here
        ## TODO Figure out how to have this method interrupt if necessary
        pass