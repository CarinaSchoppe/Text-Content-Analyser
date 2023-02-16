import os
from openie import StanfordOpenIE  # pip install pyopenie
import cleaning

do_cleaning = False
key_words = dict()
without_keywords = False

# nutzen der stanford analyse
def stanford_analysis(buch: dict):
    analysis_results = dict()
    print("\nStart analysis of results!\n")
    for header, text in buch.items():
        text.replace(":!:", "")
        #erstelle die analye für die weiligen abschnitte die gefiltert wurden
        for result in generate_analysis(text):
            for key, information in result.items():  # dict()
                # falls bereits vorhanden im dict überspringen
                if header in analysis_results and result in analysis_results[header]:
                    continue
                    # läde die einzelnen werte in ein dict eintragen falls diese noch nicht vorhanden sind
                    print("pure,", without_keywords)
                if not without_keywords:
                    for word in key_words[key]:
                        if word in information:
                            if header in analysis_results and result not in analysis_results[header]:
                                analysis_results[header].append(result)
                            else:
                                analysis_results[header] = [result]
                            break
                else:
                    if header in analysis_results and result not in analysis_results[header]:
                        analysis_results[header].append(result)
                    else:
                        analysis_results[header] = [result]

    print("\nAnalysis finished!\n")
    #cleaning aktivieren falls gewünscht
    if do_cleaning:
        analysis_results = cleaning.cleanup(analysis_results)
        print("cleaning done!")
        #alte datei enfernen falls vorhanden
    try:
        print("removed old file in standford output")
        os.remove("result.txt")
    except FileNotFoundError:
        pass
    #schreiben der ergebnisse in eine datei
    with open('result.txt', 'w', encoding="utf-8") as file:
        for key, value in analysis_results.items():
            #seperriere die einzelnen abschnitte in eigenen format
            file.write(key + "\n")
            for item in value:
                file.write("        " + str(item) + "\n")
            file.write("\n")
    print("\ndone saving!\n")
    return analysis_results


# https://stanfordnlp.github.io/CoreNLP/

# from: https://github.com/philipperemy/stanford-openie-python

properties = {
    "openie.affinity_probability_cap": 2 / 3,  # default 1/3
}


#nutzt die stanford analyse NLP analysis
def generate_analysis(text: str):
    with StanfordOpenIE(properties=properties) as client:
        text = text.replace('\n', ' ').replace('\r', '')
        analysis = client.annotate(text)
        return analysis
