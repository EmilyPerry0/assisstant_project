import subprocess
import os

os.environ["ESPEAK_DATA_PATH"] = "/opt/homebrew/share/espeak-ng-data"


class PiperTTS:
    def __init__(self, model_path, player="aplay"):
        """
        :param model_path: Full path to the .onnx Piper voice model
        :param player: Command used to play audio (e.g., 'aplay', 'ffplay', or 'mpg123')
        """
        self.model_path = model_path
        self.player = player

    def say(self, text, output_path="output.wav"):
        # Run Piper TTS and generate speech
        subprocess.run([
            "piper",
            "--model", self.model_path,
            "--text", text,
            "--output_file", output_path
        ])

# tts = PiperTTS(model_path="models/en_GB-cori-medium.onnx")

# # Speak something
# tts.say("Hello, I am your virtual assistant.")
