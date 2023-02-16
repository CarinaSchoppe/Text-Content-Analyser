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

    answers[title] = openai_object["choices"][0]["text"].replace("\n", "")

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
        headertext = "title;investors;startup;money raised\n"
        file.write(headertext)
        for title, answer in answers.items():
            file.write(title + ";" + answer[0] + ";" + answer[1] + ";" + answer[2] + "\n")


input = {"INFOTEXT": """Polish startup Plenti picks up €5 million to build rental and subscription marketplace for electronic devices
Patricia Allen
By
Patricia Allen
February 9, 2023
 Share

Polish startup Plenti is helping push forward a circular approach to using electronic devices. The team has just secured €5 million to build a marketplace that offers access to electronic devices on a subscription and rental basis. 

The circular economy is spinning ahead. While more and more people look for more sustainable, and cost-effective, ways to consume, tech innovation is helping make it happen. Through subscription-based payment solutions, rental options and refurbished/second-hand marketplaces, it’s becoming easier for Europeans to access the goods they want with a minimal environmental impact.

Electronic devices are big polluters – and we’re pretty wasteful with them. As tech development continues to move fast, for some users many devices become seen as disposable when a newer model comes to market and simply tossed away despite still being usable. At the same time, accessing the latest tech devices isn’t accessible to others – high costs being the principal barrier.

Across Europe, we’ve seen a couple of different marketplaces aim to address this – offering subscription-based solutions or refurbished models. Polish player Plenti is getting in on the action and has just secured a new investment.

Funding details
€5 million was raised in a seed round
The round was led by 4growth VC, with the participation of Montis Capital and NIF
New and existing business angels also participated
Founded by Wojciech Rokosz, Karol Klimas, and Wojciech Wójtowicz, Plenti offers access to the latest devices on demand and allows users to use them without forcing ownership. It means users can try beefier they buy, use what they need when they need, and tech devices have a reduced environmental impact. Via the platform, consumers can access game consoles, phones, smartwatches, laptops, VR headsets, air purifiers, autonomous vacuum cleaners, coffee machines, and even pizza ovens. 

Wojciech Rokosz, CEO & co-founder of Plenti: “Over the last four years we’ve proven that consumers and entrepreneurs value access to their devices over ownership. We’ve developed a platform that solves the issue on the demand side. Now we are introducing the solution for the supply side, that allows us to remain asset-light, entrepreneurs to earn on device rentals, and end-users to have even easier access to the gear they need. With the trust, and the capital from our investors we can continue to develop our marketplace in Poland and get ready to expand in Europe next year.”

The Polish startup operates on a subscription basis, offering durations from 1 -12 months and users pay just for what they use. More and more consumers are hopping on the rental trend, encouraged by the circular model and the reduced financial burden. Plenti wants to go one step further and sets itself apart by targeting entrepreneurs and companies with its PlentiPartners programme.

With PlentiPartners, an entrepreneur purchases the devices that are then leased back to Plenti, which pays them a monthly fee. The devices are fully insured and offered to consumers and a Partner retains control of their device. At the end of the rental period, Plenti might either buy devices from a partner or return them. 

Through providing a range of devices – from phones to coffee machines – Plenti offers companies and consumers alike democratised access to the latest tech. The startup reports that the most popular option is the 12-month subscription offer and gaming consoles and VR headsets are the most popular category, accounting for over 30% of rentals. 

Marcin Jaszczuk, managing partner of 4growth VC: “The idea behind Plenti fits perfectly into current market trends such as the circular economy and a shift in consumer behaviour from ownership towards rental of the electronic equipment. The company operates in a rapidly growing market and its business model is highly scalable. Combined with the competence and persistence of the founders of the company, this gives a great opportunity for success.”

With this new investment, the team plans to roll out its PlentiPartners programme, which is currently open to sole proprietors and companies registered in Poland. Plenti will also expand the team in order to meet up with growing demand and product development. 

 Łukasz Dziekoński, managing partner of Montis Capital: “Plenti has been fighting against electro waste by redefining consumption patterns and shifting from traditional source, use, waste, journey. Our goal is to invest in the best companies that contribute to sustainability, which includes responsible consumption and waste management. We are pleased to support Wojtek and their team as they introduce consumers to circular economy in the most convenient way possible.”"""}


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

        # schreibe die ergebnisse in eine datei
    write_to_file(answers)


calculate(input)
