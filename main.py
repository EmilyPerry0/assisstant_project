from google import genai
from dotenv import load_dotenv
from pvrecorder import PvRecorder
from collections import deque

import os
import pvporcupine
import whisper
import pvcobra
import logging
import argparse

import numpy as np

class Assisstant:
    def __init__(self):

        # set to true for debugging purposes, false otherwise
        self.log = logging.getLogger("assisstant")

        # used to detect wake word
        self.porcupine = pvporcupine.create(
        access_key=os.environ.get("PV_ACCESS_KEY"),
        keyword_paths=[os.environ.get("WAKE_WORD_MODEL_PATH")],
        )

        # used to detect speech activity
        self.cobra = pvcobra.create(access_key=os.environ.get("PV_ACCESS_KEY"),)

        # setup the local whisper model
        self.model =  whisper.load_model(os.environ.get("WHISPER_MODEL"))


        '''
        RECORDER SETUP
        '''
        # 1 sec = 16,000 / 512
        self.frame_length = 512
        self.sample_rate = 16000
        
        # voice activity sensitivity
        self.vad_mean_probability_sensitivity = float(os.environ.get("VAD_SENSITIVITY"))
        # setup audio input
        self.recorder = PvRecorder(device_index=-1, frame_length=self.frame_length)
        self.recorder.start()
        max_window = 3
        self.window_size = self.sample_rate * max_window
        self.samples = deque(maxlen=self.window_size*6)
        # why is this 25
        self.vad_samples = deque(maxlen=25)
        self.is_recording = False

    def listen(self):
        """Listens from the mic and calculates the probability that it heard speech

        Args:
            none

        Returns:
            List[int]: the recorded sounds
        """
        data = self.recorder.read()
        vad_probability = self.cobra.process(data)
        self.vad_samples.append(vad_probability)
        return data

    def transcribe_command(self):
        """Listen to the audio of a command until speech stops, then transcribe it
        Args:
            none
        Returns:
            string: the transcribed text
        """
        while len(self.samples) < self.window_size or np.mean(self.vad_samples) >= self.vad_mean_probability_sensitivity:
            data = self.listen()
            self.samples.extend(data)

        # process the speech it heard
        transcriber_samples = np.array(self.samples, np.int16).flatten().astype(np.float32) / 32768.0

        # TODO:work on multi language capabilities
        # TODO: look into initial prompting
        result = self.model.transcribe(audio=transcriber_samples, language='en', fp16=False)
        self.log.debug("Command transcribed! You said: " + result.get("text"))
        return result.get("text")


    def listen_for_wake_word(self):
        """Continuous listening for a spoken wake word

        Args:
            none

        Returns:
            none 
        """
        self.log.debug("Listening for wake word...")
        try:
            while True:
                data = self.listen()
                if self.porcupine.process(data) >= 0: # wake word detected
                    self.log.debug("Wake word detected! Recording command...")
                    self.samples.clear()
                    self.transcribe_command()
                    self.log.debug("Listening for wake word again...")

        except KeyboardInterrupt:
            self.recorder.stop()
        finally:
            self.porcupine.delete()
            self.recorder.delete()
            self.cobra.delete()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug', help='Debug flag', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = get_args()
    load_dotenv()

    # setup logging
    logging.getLogger("assisstant").setLevel(logging.DEBUG if args.get('debug') else logging.WARNING)
    logging.basicConfig()

    my_ai_assisstant = Assisstant()
    my_ai_assisstant.listen_for_wake_word()

if __name__ == "__main__":
    main()