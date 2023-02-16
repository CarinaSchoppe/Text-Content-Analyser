import os
from transformers import pipeline

use = True
model = classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ["investor", "investee", "amount of money", "startup funding", "investment"]

# abspeichern in einem dict:

minimum_value = .95
minimum_keywords = 3


def dict_converter(buch):
    new = dict()
    for title, text in buch.items():
        new[title] = text.split(":!:")
    return new


def perform_analysis(buch):
    if not use:
        return
    buch = dict_converter(buch)
    print("neues buch: ", buch)
    item_dict = dict()
    for title, article in buch.items():
        item_dict[title] = []
        if len(article) == 0:
            continue
        for block in article:
            if len(block) == 0:
                continue
            res = classifier(block, candidate_labels, multi_label=True)  # dict {'sequence': 'sentence', 'labels': [..], 'scores': [0.12795370817184448, 0.011927961371839046, 0.0006385071901604533]}
            item_dict[title].append(res)
            print(res)
    return item_dict


def analyse(item_dict: dict):
    results = dict()
    for title, analyse in item_dict.items():
        results[title] = []
        for result in analyse:
            amount = 0
            for score in result["scores"]:
                if score > minimum_value:
                    amount += 1
            if amount >= minimum_keywords:
                results[title].append(result["sequence"])
        if len(results[title]) == 0:
            del results[title]
    return results


def write_file(item_dict: dict):
    try:
        print("removed old file in transformers output")
        os.remove("results_transformers.txt")
    except FileNotFoundError:
        pass
    with open("results_transformers.txt", "w", encoding="UTF-8") as file:
        for title, absätze in item_dict.items():
            file.write(title + "\n")
            for absatz in absätze:
                file.write("      " + absatz + "\n")
            file.write("\n\n")

    print("Transformers finished!\nFiles saved!")


def transformer_analysis(buch: dict):
    analysis_result = perform_analysis(buch)
    results = analyse(analysis_result)
    write_file(results)
