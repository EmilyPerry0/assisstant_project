from google import genai
from dotenv import load_dotenv
from pvrecorder import PvRecorder
from collections import deque

import os
import pvporcupine
import whisper
import pvcobra

import numpy as np

class Assisstant:
    def __init__(self, dev):

        # set to true for debugging purposes, false otherwise
        self.dev_flag = dev

        # used to detect wake word
        self.porcupine = pvporcupine.create(
        access_key=os.environ.get("ACCESS_KEY"),
        keyword_paths=[os.environ.get("WAKE_WORD_MODEL_PATH")],
        )

        # used to detect speech activity
        self.cobra = pvcobra.create(access_key=os.environ.get("ACCESS_KEY"),)

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
        self.recoder = PvRecorder(device_index=-1, frame_length=self.frame_length)
        self.recorder.start()
        max_window = 3
        self.window_size = self.sample_rate * max_window
        self.samples = deque(maxlen=window_size*6)
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
        data = self.recoder.read()
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
        return result.get("text")


    def listen_for_wake_word(self):
        """Continuous listening for a spoken wake word

        Args:
            none

        Returns:
            none 
        """
        try:
            while True:
                data = self.listen()
                if self.porcupine.process(data) >= 0: # wake word detected
                    self.samples.clear()
                    self.transcribe_command()

        except KeyboardInterrupt:
            self.recorder.stop()
        finally:
            self.porcupine.delete()
            self.recoder.delete()
            self.cobra.delete()


def main():
    load_dotenv()
    my_ai_assisstant = Assisstant(dev=True)
    my_ai_assisstant.listen_for_wake_word()

if __name__ == "__main__":
    main()