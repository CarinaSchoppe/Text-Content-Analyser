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
    openai_object = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0)

    answers[title] = openai_object["choices"][0]["text"].replace("\n", "").replace(",", ";")

    print("title", title, "answer: " + answers[title])
    investors = answers[title].split("Startup: ")[0].replace("Investors: ", "")
    startup = answers[title].split("Startup: ")[1].split("Amount of Money Raised: ")[0]
    money = answers[title].split("Amount of Money Raised: ")[1]

    answers[title] = (investors, startup, money)
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
        headertext = "title,investors,startup,money raised\n"
        file.write(headertext)
        for title, answer in answers.items():
            file.write(title.replace(",", ";") + "," + answer[0] + "," + answer[1] + "," + answer[2] + "\n")
    print("writing to file completed.")


# berechnet und schreibt die analyse werte
def calculate(input_data):
    if not use:
        return
    # gehe durch alle ergebnisse durch und analysiere diese
    for title, text in input_data.items():
        # packe den fragetext vor den infotext
        prompt = pre_text + title + text
        # generiere die analyse
        generate_response(title, prompt)
    print("calculation with openai GPT-3 done.\nWriting to file")

        # schreibe die ergebnisse in eine datei
    write_to_file(answers)


