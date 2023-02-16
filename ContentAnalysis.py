import os
import Stanford as stanford
import cleaning

words_to_contain = tuple()
stanford_only = False
intense = True
skip_stanford = False
stanford_only_sentences = True


# content analye
def content_analysis(buch: dict):
    # die gefilterten items
    filtered_items = dict()
    # jedes element in dem block splitten in titel und text
    for header, item in buch.items():
        # den text in absätze unterteilen
        for block_sentence in item.split(":!:"):
            # auf sätze filtern oder auf absätze
            important = cleaning.filter(block_sentence, words_to_contain, filtered_items, header, stanford_only, intense)
            if important:
                for sentence in block_sentence.split("."):
                    cleaning.filter(sentence, words_to_contain, filtered_items, header, stanford_only, intense, False, block_sentence)

    # entfernen der alten datei falls vorhanden
    try:
        print("removed old file in content analysis output")
        os.remove("scraped.txt")
    except FileNotFoundError:
        pass

    print(filtered_items)

    # schreiben der ergebnisse in eine datei
    with open("scraped.txt", "w", encoding="UTF-8") as file:
        for header in filtered_items:
            file.write(f"{header}\n\n")
            for absatz, object in filtered_items[header].items():
                sentences = absatz.split(". ")
                try:
                    for sentence in sentences:
                        if sentence == "":
                            continue
                        file.write(f"      {sentence}.\n")
                    for keyword, sentences in object.items():
                        file.write(f"             {keyword}:\n")
                        for sentence in sentences:
                            file.write(f"                    {sentence}.\n")

                except UnicodeEncodeError:
                    print("Found Unicode character that cant be encoded: skipping")
                finally:
                    file.write("\n")
            file.write("\n\n")

    print("Content Analysis finished!\nFiles saved!")
    if not skip_stanford:
        # fortfahren mit der stanford analyse
        stanford.stanford_analysis(cleaning.sentence_creator(filtered_items, stanford_only_sentences, stanford_only))
