from google import genai

import os
import logging

class Gemini:
    def __init__(self):
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=gemini_api_key)
        self.chat = client.chats.create(model='gemini-2.0-flash-001')

        # give gemini some basic info / background knowledge
        starting_prompt_file = open("prompts/starting_prompt.txt", "r")
        starting_prompt = starting_prompt_file.read()
        starting_prompt_file.close()
        saved_info_file = open("saved_information.txt", "r")
        saved_info = saved_info_file.read()
        saved_info_file.close()
        self.chat.send_message(starting_prompt + saved_info)

        # set up logger
        self.log = logging.getLogger("assisstant")

    def query_gemini(self, sentence):    
        response = self.chat.send_message(sentence).text
        self.log.debug("gemini query response: " + response)

    def save_important_info(self, sentence):
        important_info_prompt_file = open("prompts/important_info_prompt.txt", "r")
        important_info_prompt = important_info_prompt_file.read()
        important_info_prompt_file.close()
        response = self.chat.send_message(important_info_prompt + sentence).text[0:-1]
        self.log.debug("gemini's reponse to whether it should remember info from the command: " + response)

        if response.lower() == "yes": # summarize what's important and save it
            summarized_important_info_prompt_file = open("prompts/summarized_important_info_prompt.txt", "r")
            summarized_important_info_prompt = summarized_important_info_prompt_file.read()
            summarized_important_info_prompt_file.close()

            summarized_important_info = self.chat.send_message(summarized_important_info_prompt + sentence).text
            important_info_file = open("saved_information.txt", "w")
            important_info_file.write(summarized_important_info)
            important_info_file.close()
        elif response.lower() == "no":
            self.log.debug("why gemini said no: " + self.chat.send_message("please explain why you said no.").text)
        else:
            self.log.debug("gemini gave an invalid response: " + response)

