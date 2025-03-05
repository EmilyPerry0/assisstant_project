import speech_recognition as sr

from google import genai

dev = True

def listen_and_store(chat, wake_word="computer"):
    """
    Listens for a wake word, then records and stores the following sentence.

    Args:
        chat: the gemini chat instance
        wake_word: The word that triggers the recording.
        output_file: The name of the file to store the sentences.
    """

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise

        while True:
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio).lower() #lower case to make wake word easier to detect.

                if wake_word in text:
                    print("Wake word detected. Listening for sentence...")
                    audio = recognizer.listen(source) #listen for next audio
                    sentence = recognizer.recognize_google(audio)
                    print("sentence recorded!")
                    query_gemini(chat, sentence)
                    

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except Exception as e:
                print(f"An unexpected error occured: {e}")


# this returns just the text of the query
def query_gemini(chat, sentence):    
    response = chat.send_message(sentence).text
    print(response)
    save_important_info(chat, sentence)

def save_important_info(chat, sentence):
    important_info_prompt_file = open("prompts/important_info_prompt.txt", "r")
    important_info_prompt = important_info_prompt_file.read()
    important_info_prompt_file.close()
    response = chat.send_message(important_info_prompt + sentence).text[0:-1]
    print(response)
    if response.lower() == "yes":
        summarized_important_info_prompt_file = open("prompts/summarized_important_info_prompt.txt", "r")
        summarized_important_info_prompt = summarized_important_info_prompt_file.read()
        summarized_important_info_prompt_file.close()

        summarized_important_info = chat.send_message(summarized_important_info_prompt + sentence).text
        important_info_file = open("saved_information.txt", "a")
        important_info_file.write(summarized_important_info)
        important_info_file.close()
    elif dev:
        print(chat.send_message("please explain why you said no.").text)

def init_gemini_chat():
    api_file = open("api_key.txt", "r")
    api_key = api_file.read()
    api_file.close()

    client = genai.Client(api_key=api_key)
    chat = client.chats.create(model='gemini-2.0-flash-001')

    starting_prompt_file = open("prompts/starting_prompt.txt", "r")
    starting_prompt = starting_prompt_file.read()
    starting_prompt_file.close()

    saved_info_file = open("saved_information.txt", "r")
    saved_info = saved_info_file.read()
    saved_info_file.close()

    chat.send_message(starting_prompt + saved_info)

    return chat


def main():
    chat = init_gemini_chat()
    # print(chat.send_message('what is the weather right now?').text)
    listen_and_store(chat)


if __name__ == "__main__":
    main()