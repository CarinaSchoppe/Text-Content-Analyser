import ContentAnalysis as content_analysis
import OpenAI as ai
import Scraper


def main():
    # anzahl Seiten auf eu startups die angeschaut werden sollen
    Scraper.look_out = 1
    Scraper.infinite = False  # sollen alle möglichen seiten durchsucht werden?

    # welche begriffe sollen in der stanford filterung bei den jeweiligen beziehungen mindestens vorhanden sein
    # stanford.key_words = {"object": {"money", "company", "invest", "name"},
    # subject": {"money", "company", "name", "invest"},
    # "relation": {"invest", "raise", "funded", "funding"}}
    # Skip stanford analysis
    content_analysis.skip_stanford = True
    # welche beziehungen gibt es in der content_analysis analyse und welche begriffe sind dafür trigger und in welcher höufigkeit sollen diese existieren
    content_analysis.words_to_contain = (3, {"£", "money", "€", "million", "raised", "funded", "$", "company", "business", "investor", "investing", "invested", "investing", "investment"})
    # es darf nur ein oder mehrere einträge pro artikel zu einer kategorie geben
    content_analysis.intense = False  # False=es kann mehrere wichtige absätze pro artikel geben, True = pro titel gibts nur einen absatz der wichtig ist
    # content_analysis analyse und filter überspringen
    content_analysis.stanford_only = False
    # mehrfache abstufungen in elementen der beziehungen rausfiltern
    # stanford.do_cleaning = True
    # stanford pure analysis without keywords
    # stanford.without_keywords = False
    # analysiere nur die wichtigen sätze für Stanford von der content_analysis
    content_analysis.stanford_only_sentences = True  # True = nimm den satz der z.B. bei investment: "...." steht bei False nimm den ganzen Absatz für Stanford
    """
    # Transformer Modul nutzen
    transformer.use = True
    # Transformer Model label
    transformer.candidate_labels = ["investors", "funding", "investment"]
    # Transformer minimum schwellenwert
    transformer.minimum_value = .95
    # minimum Anzahl an Keywords die den Schwellenwert überschreiten müssen
    transformer.minimum_keywords = 3
    """
    # sammle alle einträge von eu startups raus
    buch = Scraper.load_contents()  # dict header, items -> text
    # starte die analysen
    # Transformer
    # transformer.transformer_analysis(buch)
    # Contentbase
    # OPENAI API KEY
    ai.KEY = "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"
    # use openAI GPT-3 Davinci Model
    ai.use = True
    # startet die analyse durch openAI
    ai.calculate(buch)

    content_analysis.content_analysis(buch)


if __name__ == "__main__":
    main()
