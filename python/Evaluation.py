import os
import re
import xml.etree.ElementTree as elementtree

import openai

openai.api_key = "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"
dict_entity = dict()
dict_semantic = dict()
debug = False
dict_answers = dict()


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
        if debug:
            print(f"text={file_text} id={id} result={dict_entity[file_text][id]}")
    for child in root:
        if "SemanticRelations" not in child.tag:
            continue
        dependent = dict_entity[file_text][child.attrib["Dependent"]]
        governor = dict_entity[file_text][child.attrib["Governor"]]
        relation = child.attrib["Relation"]
        id = child.attrib["{http://www.omg.org/XMI}id"]
        # governor relation dependent
        dict_semantic[file_text][id] = (governor, relation, dependent)
        print(dict_semantic)
        exit()
        if debug:
            print(f"text={file_text} id={id} result={dict_semantic[file_text][id]}")


def format_converter(semantic_dict, document):
    for text, value in semantic_dict.items():
        results = []
        for id, triple in value.items():
            # old format: governor relation dependent new format: <triplet> governor <sub> dependent <obj> relation
            if debug:
                print(f"old: {triple[0]} {triple[1]} {triple[2]}")
                print(f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}")
            result = f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}"
            results.append(result)
        # reperate all results in result in one string seperated by "  "
        final_string = "  ".join(results)
        file_saver(final_string, document)


def convert_chat_gpt_answer(input: str, answer: str):
    global dict_answers
    # answer format = (Ent; relation; entity)
    # convert into differeent variables
    answer = re.sub(r"[\(\)]", "", answer)
    answer = answer.split(";")
    entity = answer[0]
    relation = answer[1][1:]
    entity2 = answer[2][1:]
    if (input in dict_answers):
        # get the len of elements in the dict_answers[input] and add 1 to it
        dict_answers[input][len(dict_answers[input])] = (entity, relation, entity2)
    else:
        input_dict = dict()
        input_dict[0] = (entity, relation, entity2)


def file_saver(text, document):
    with open(f"../documents/results/{document}.csv", "a", encoding="UTF-8") as file:
        file.write(text + "\n")


def generate_response(input_text, prefix=""):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prefix + input_text}]
    )
    answer = completion.choices[0]["message"]["content"]
    convert_chat_gpt_answer(input=input_text, answer=answer)


def main():
    files = [filename for filename in os.listdir("../documents/xmi") if filename.endswith(".xmi")]
    for filename in files:
        extract_values_from_file(filename)
    texts = {text for text in dict_entity.keys()}
    file_saver("triplets", "ai_results")
    file_saver("triplets", "self_results")
    for text in texts:
        generate_response(text)
    format_converter(dict_semantic, "self_results")
    format_converter(dict_answers, "ai_results")


if __name__ == "__main__":
    main()
    # TODO:
