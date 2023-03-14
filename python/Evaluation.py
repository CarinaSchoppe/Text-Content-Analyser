import os
import re
import xml.etree.ElementTree as elementtree

import openai

openai.api_key = "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"
dict_entity = dict()
dict_semantic = dict()
debug = True
dict_answers = dict()


def extract_values_from_file(file, path="../documents/xmi/"):
    """
    dict_ent -> "text" -> dict -> "id" ->  value
    dict_sem -> "text" -> dict -> "id" -> (object, relation, value)
    """
    tree = elementtree.parse(path + file)
    root = tree.getroot()
    file_text = "".join(open(path + file, "r", encoding="UTF-8").readlines()).split('sofaString="')[1].split('"')[0]
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
    print("file conversion for file {} done".format(document))


def convert_chat_gpt_answer(input_text: str, output: str):
    # answer format = (Ent; relation; first_entity)
    # convert into different variables
    answers = output.split("\n")
    valid_answers = []
    valid = True
    for answer in answers:
        if answer == "" or answer == " " or answer == "\n" or answer is None:
            continue
        try:
            answer = re.sub(r"[\(\)]", "", answer)
            answer = answer.split(",")
            first_entity = answer[0]
            relation = answer[1][1:]
            second_entity = answer[2][1:]
            valid_answers.append((first_entity, relation, second_entity))

        except Exception as exception:
            print("---------------------------------------------------------------------------")
            print(exception)
            valid = False
            print(f"because: answer from chat gpt was not in the right format, format: {output}")
            print(f"input was: {input_text}")
            print("---------------------------------------------------------------------------")
            break
    if valid:
        for answer in valid_answers:
            first_entity, relation, second_entity = answer
            if input_text in dict_answers:
                # get the len of elements in the dict_answers[input] and add 1 to it
                dict_answers[input_text][len(dict_answers[input_text])] = (first_entity, relation, second_entity)
            else:
                input_dict = dict()
                input_dict[0] = (first_entity, relation, second_entity)
                dict_answers[input_text] = input_dict
        if debug:
            print("worked", "input:", input_text, "answer:", answer)


def file_saver(text, document):
    if text == "" or text == " " or text == "\n" or text is None:
        return
    with open(f"../documents/results/{document}.csv", "a", encoding="UTF-8") as file:
        file.write(text + "\n")


def comparison_of_results(answers_dict, semantic_dict):
    # compare the two dictionaries based on if a key in semantic dict is also present in answers_dict if not delete it
    for text in semantic_dict.keys():
        if text not in answers_dict:
            del semantic_dict[text]


def generate_response(input_text, prefix=f"""
Act like a data engineer. You need to extract relationships in the form of triplets from articles that deal with investment rounds in the start-up scene. I will give you some examples so you know what to extract. Do you understand?

1. example: “Founded in 2015, the banking app, which focuses exclusively on the Nordics, raised €13 million and expanded to Norway back in February.” 
In this case you should extract: (€13 million, was received, February) --> (money, was received, date)
And you are only allowed to use the relation "was received"!

2. example: “BetterUp, a US-based rival CoachHub, recently raised a $103 million Series C.” 
In this case you should extract: ($103 million, in round, Series C) --> (money, in round, funding round)
And you are only allowed to use the relation "in round"!


3. example: “The €1.86 million investment round of Trustmary consisted of a €1.15 million equity investment from Vendep Capital, a Northern European SaaS focused venture capital company, and a €751K loan from Business Finland”

In this case you should extract: 
(Trustmary, received total, €1.86 million)
(€1.86 million, has investment part, €1.15 million)
(€1.86 million, has investment part, €751k)
(Vendep Capital, invests part, €1.15 million)
(Business Finland, invests part, €751k)


4. example: “Founded in 2015, the Fineway has just increased its Series A round raised in early November with an additional €6 million, bringing the total round size to €13 million.”
(Fineway, received, €6 million)
(€6 million, was received, November)
(€6 million, in round, Series A)
(Fineway, received total, €13 million)
(€13 million, in round, series A)


Analyse this text:""", postfix="""just give the answers in the matching format and only the (enitity,relation,entity) answers no other sentence should be in the answer so without the sentence 'Here are the extracted triplets from the text'"""):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prefix + input_text + postfix}]
    )
    answer = completion.choices[0]["message"]["content"]
    convert_chat_gpt_answer(input_text=input_text, output=answer)


def main():
    files = [filename for filename in os.listdir("../documents/xmi") if filename.endswith(".xmi")]
    for filename in files:
        extract_values_from_file(filename)
    if debug:
        print("extraction and conversion done")

    texts = {text for text in dict_entity.keys()}
    if debug:
        print("text extraction done")
    try:
        for file in os.listdir("../documents/results"):
            os.remove(os.path.join("../documents/results", file))
    except Exception as _:
        pass
    if debug:
        print("file deletion done")
    file_saver("triplets", "ai_results")
    file_saver("triplets", "self_results")
    if debug:
        print("file creation done")
    for text in texts:
        generate_response(text)
    if debug:
        print("ai answers done")
    comparison_of_results(answers_dict=dict_answers, semantic_dict=dict_semantic)
    if debug:
        print("comparison of results done")
    format_converter(dict_semantic, "self_results")
    format_converter(dict_answers, "ai_results")
    print("code completed")


if __name__ == "__main__":
    main()
