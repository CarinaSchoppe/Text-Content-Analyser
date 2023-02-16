import csv
import os

import openai

# value ob das modell genutzt werden soll
use = True
# boolean ob das system die daten in eine datei schreiben soll
write_to_file = True
# API KEY für OPENAI
KEY = "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"
# API KEY für OPENAI
openai.api_key = KEY

# analysetext der vor jede antwort gepackt wird.
pre_text = "tell me  the investors, the name of the startup and the amount of money raised from this text:\n\n"

# ergebnis dictionary
answers = dict()


# funktion die den response über openai generiert
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
    with open("answers.csv", "w", encoding="UTF-8") as file:
        # write the dictionary into an csv file
        writer = csv.writer(file)
        headertext = "title;answer"
        writer.writerow(headertext)
        for title, answer in answers.items():
            writer.writerow([title, answer])


# berechnet und schreibt die analyse werte
def calculate(input_data):
    if not use:
        return
    # gehe durch alle ergebnisse durch und analysiere diese
    for title, text in input_data.items():
        # packe den fragetext vor den infotext
        prompt = pre_text + text
        #generiere die analyse
        generate_response(title, prompt)
        #schreibe die ergebnisse in eine datei
    write_to_file(answers)
