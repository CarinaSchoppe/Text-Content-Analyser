import os
import xml.etree.ElementTree as elementtree

import openai

dict_entity = dict()
dict_semantic = dict()
debug = False


def generate_response(input_text, prefix=""):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prefix + input_text}]
    )
    print(completion)
    return completion.choices[0]["text"]


def extract_values_from_file(filepath, path="../documents/xmi/"):
    """
    dict_ent -> "text" -> dict -> "id" ->  value
    dict_sem -> "text" -> dict -> "id" -> (object, relation, value)
    """
    tree = elementtree.parse(path + filepath)
    root = tree.getroot()
    file_text = "".join(open(path + filepath, "r", encoding="UTF-8").readlines()).split('sofaString="')[1].split('"')[0]
    dict_entity[file_text] = dict()
    dict_semantic[file_text] = dict()
    # extraction of entities
    for child in root:
        if "NamedEntity" not in child.tag:
            continue
        # if "value" in child.attrib and child.attrib["value"] == "REGEX":
        #     continue TODO: should be contained?
        id = child.attrib["{http://www.omg.org/XMI}id"]
        begin = int(child.attrib["begin"])
        end = int(child.attrib["end"])
        text = file_text[begin:end]
        dict_entity[file_text][id] = text
        print(f"text={file_text} id={id} result={dict_entity[file_text][id]}" if debug else "", end="\r")
    for child in root:
        if "SemanticRelations" not in child.tag:
            continue
        dependent = dict_entity[file_text][child.attrib["Dependent"]]
        governor = dict_entity[file_text][child.attrib["Governor"]]
        relation = child.attrib["Relation"]
        id = child.attrib["{http://www.omg.org/XMI}id"]
        # governor relation dependent
        dict_semantic[file_text][id] = (governor, relation, dependent)
        print(f"text={file_text} id={id} result={dict_semantic[file_text][id]}" if debug else "", end="\r")


def evaluate(gold_answers, ai_answers):
    pass


def main():
    files = [filename for filename in os.listdir("../documents/xmi") if filename.endswith(".xmi")]
    for filename in files:
        extract_values_from_file(filename)


if __name__ == "__main__":
    main()
