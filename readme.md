# download all dependencies
type `pip install -r requirements.txt` into your console to get all dependencies for this project.

# setup your own .env file
use the provided `.env.example` file as a template and add your own things to it

# create picovoice account
go to the [picovoice website](https://console.picovoice.ai/) and create your pv access key. add this to your `.env` file.

# train wakeword on picovoice
choose and train a wake word with [Picovoice](https://console.picovoice.ai/ppn). download the appropriate (`.ppn`) file for your os. Once you have downloaded your wake-word `.zip`, unzip the file and move the `.ppn` file to the `models` folder.

# select your whisper local model
set the `WHISPER_MODEL` variable in the `.env` file according to what model you want to use. available options can be found [here](https://github.com/openai/whisper/blob/main/model-card.md). (ex: tiny.en)

# usage
```
python3 main.py [-d]
```
Options:\n
[-d/--debug]: enables command line output useful for debugging