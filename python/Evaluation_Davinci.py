import os
import re
import time
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
    file_text = file_text.replace('&amp;', ' ')
    print(file_text)
    # print('\n shekhar1 \n')

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

        # print('\n id: ', id)
        # print('\n begin: ', begin)
        # print('\n end: ', end)
        # print('\n text: ', text)

        if debug:
            # print('\n hello \n')
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
            # print('\n hello2 \n')
            print(f"text={file_text} id={id} result={dict_semantic[file_text][id]}")
            # print(dict_semantic[file_text])


def format_converter(dictionary, document):
    # return if dictionary is empty
    if not dictionary:
        return
    for text, value in dictionary.items():
        results = []
        if type(value) is not dict:
            continue

        for id, triple in value.items():
            # old format: governor relation dependent new format: <triplet> governor <sub> dependent <obj> relation
            if debug:
                # print('\n hello3 \n')
                print(f"old: {triple[0]} {triple[1]} {triple[2]}")
                # print('\n hello4 \n')
                print(f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}")
            result = f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}"
            results.append(result)
        # reperate all results in result in one string seperated by "  "
        final_string = "  ".join(results)
        file_saver(final_string, document)
    print("file conversion for file {} done".format(document))
    # print(file_saver)


def convert_chat_gpt_answer(input_text: str, output: str):
    # answer format = (Ent; relation; first_entity)
    # convert into different variables
    answers = output.split("\n")
    valid_answers = []
    for answer in answers:
        if answer == "" or answer == " " or answer == "\n" or answer is None:
            continue
        try:
            # remove everything before the first "(" and after the last ")"
            answer = answer[answer.find("("):]
            answer = re.sub(r"[\(\)]", "", answer)
            answer = answer.split(",")
            first_entity = answer[0]
            relation = answer[1][1:]
            second_entity = answer[2][1:]
            valid_answers.append((first_entity, relation, second_entity))
        except Exception as exception:
            print("---------------------------------------------------------------------------")
            print(exception)
            print(f"because: answer from chat gpt was not in the right format, format: {output}")
            print(f"exact mistake: {answer}")
            print(f"input was: {input_text}")
            print("---------------------------------------------------------------------------")
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
        print("worked", "input:", input_text, "answer:", valid_answers)


def file_saver(text, document):
    if text == "" or text == " " or text == "\n" or text is None:
        return
    with open(f"../documents/results/{document}.csv", "a", encoding="UTF-8") as file:
        file.write(text + "\n")


def comparison_of_results(answers_dict, semantic_dict):
    # create a list of keys to remove from the semantic_dict
    keys_to_remove = []
    for text in semantic_dict.keys():
        if text not in answers_dict:
            keys_to_remove.append(text)
    # remove the keys from the semantic_dict
    for key in keys_to_remove:
        del semantic_dict[key]


def generate_response(input_text, prefix=None):
    prompt = """Summarise the text above in 5 sentences."""

    if prefix is not None:
        prompt += prefix

    prompt = f"{input_text}\n{prompt}"

    completion = openai.Completion.create(
        model="text-davinci-003",  # 3.5-turbo
        temperature=0,
        prompt=prompt
    )

    print(completion)

    # result = completion.choices[0]["message"]["content"]  #carinas variante
    result = completion.choices[0]["text"]  # result = completion.choices[0].message['content']

    # Das Ergebnis des letzten Prompts im dict_answers speichern
    # TODO: Nötig? dict_answers[prompt] = result

    # return prompt_results, dict_answers

    # completion = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[{"role": "user", "content": prefix + input_text}])
    # answer = completion.choices[0]["message"]["content"]
    try:
        convert_chat_gpt_answer(input_text=input_text, output=result)
    except Exception as _:
        pass
    # make the current thread sleep for 4 seconds
    time.sleep(((60 / 20) * 1) + 1)


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

    if debug:
        print("Start of evaluation")
    import Text_Evaluation as txt_eval
    txt_eval.evaluate()


if __name__ == "__main__":
    main()
