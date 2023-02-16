import openai
import os

use = True
write_to_file = True
API_KEY = "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"
openai.api_key = API_KEY

pre_text = "tell me  the investors, the name of the startup and the amount of money raised from this text:\n\n"

answers = dict()


def generate_response(title, prompt):
    answers[title] = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0)
    return answers[title]


def write_to_file(answers):
    # delete existing file with the name "answers.txt"
    if not write_to_file:
        return
    try:
        os.remove("answers.txt")
    except FileNotFoundError:
        pass
    # write the answers to a file
    with open("answers.txt", "w", encoding="UTF-8") as file:
        for title, answer in answers.items():
            file.write(title + ":\n")
            file.write("     " + answer + "\n")


def calculate(input_data):
    if not use:
        return
    for title, text in input_data.items():
        prompt = pre_text + text
        generate_response(title, prompt)
    write_to_file(answers)
