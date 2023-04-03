import os
import re
import xml.etree.ElementTree as elementtree

import openai

openai.api_key = "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"
dict_entity = dict()
dict_own_labels = dict()
debug = True
debug_full = False
dict_ai_answers = dict()


def extract_values_from_file(file, path="../documents/xmi/"):
    """
    dict_ent -> "text" -> dict -> "id" ->  value
    dict_sem -> "text" -> dict -> "id" -> (object, relation, value)
    """
    tree = elementtree.parse(path + file)
    root = tree.getroot()
    file_text = "".join(open(path + file, "r", encoding="UTF-8").readlines()).split('sofaString="')[1].split('"')[0]
    file_text = file_text.replace('&amp;', ' ')

    dict_entity[file_text] = dict()
    dict_own_labels[file_text] = dict()
    # extraction of entities
    for child in root:
        if "NamedEntity" not in child.tag:
            continue

        id = child.attrib["{http://www.omg.org/XMI}id"]
        begin = int(child.attrib["begin"])
        end = int(child.attrib["end"])
        text = file_text[begin:end]
        dict_entity[file_text][id] = text

        if debug_full and debug:
            print(f"text={file_text} id={id} result={dict_entity[file_text][id]}")

    for child in root:
        if "SemanticRelations" not in child.tag:
            continue
        dependent = dict_entity[file_text][child.attrib["Dependent"]]
        governor = dict_entity[file_text][child.attrib["Governor"]]
        relation = child.attrib["Relation"]
        id = child.attrib["{http://www.omg.org/XMI}id"]
        # governor relation dependent
        dict_own_labels[file_text][id] = (governor, relation, dependent)
        if debug_full and debug:
            print(f"text={file_text} id={id} result={dict_own_labels[file_text][id]}")


def format_converter(semantic_dict, document):
    for text, value in semantic_dict.items():
        results = []
        if type(value) is not dict:
            continue
        for id, triple in value.items():
            # old format: governor relation dependent new format: <triplet> governor <sub> dependent <obj> relation
            if debug and debug_full:
                print(f"old: {triple[0]} {triple[1]} {triple[2]}")
                print(f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}")
            results.append(f"<triplet> {triple[0]} <sub> {triple[2]} <obj> {triple[1]}")
        # reperate all results in result in one string seperated by "  "
        final_string = "  ".join(results)
        file_saver(final_string, document)
    print("file conversion for file {} done".format(document))


def convert_chat_gpt_answer(input_text: str, output: str):
    # answer format = (Ent; relation; first_entity)
    # convert into different variables
    answers = output.split("\n")
    valid_answers = []
    invalid_answers = []
    for index, answer in enumerate(answers):
        if answer == "" or answer == " " or answer == "\n" or answer is None:
            continue
        try:
            # remove everything before the first "(" and after the last ")"
            clean_answer = answer
            # check if "xxx" is in any answer (lowercased) string than continue
            if "xxx" in clean_answer.lower():
                raise Exception("xxx in answer")
            answer = answer[answer.find("("):]
            answer = re.sub(r"[\(\)]", "", answer)
            answer = answer.split(",")
            first_entity = answer[0]
            relation = answer[1][1:]
            second_entity = answer[2][1:]
            if debug and debug_full:
                print(f"answer: {(first_entity, relation, second_entity)} added to valid answers")
            valid_answers.append((first_entity, relation, second_entity))
        except Exception as exception:
            invalid_answers.append(clean_answer)
            print("---------------------------------------------------------------------------")
            print(f"exception-message: {exception}")
            print(f"because answer from chat-gpt was not in the right format, format:\n{output}\n")
            print(f"exact mistake: '{clean_answer}'")
            print(f"input was: '{input_text}'")
            print("---------------------------------------------------------------------------")
    if debug:
        print(f"valid answers: {valid_answers}")
        print(f"invalid answers: {invalid_answers}")
    for answer in valid_answers:
        first_entity, relation, second_entity = answer
        if input_text in dict_ai_answers:
            # get the len of elements in the dict_answers[input] and add 1 to it
            dict_ai_answers[input_text][len(dict_ai_answers[input_text])] = (first_entity, relation, second_entity)
        else:
            input_dict = dict()
            input_dict[0] = (first_entity, relation, second_entity)
            dict_ai_answers[input_text] = input_dict
    if debug and valid_answers != []:
        print("worked", "input:", input_text, "answer:", valid_answers)


def file_saver(text, document):
    if text == "" or text == " " or text == "\n" or text is None:
        return
    with open(f"../documents/results/{document}.csv", "a", encoding="UTF-8") as file:
        file.write(text + "\n")


def comparison_of_results(answers_dict, semantic_dict):
    # create a list of keys to remove from the semantic_dict
    keys_to_remove = []
    for key_text in semantic_dict.keys():
        if key_text not in answers_dict:
            keys_to_remove.append(key_text)
    # remove the keys from the semantic_dict
    for key in keys_to_remove:
        if debug and debug_full:
            print(f"key {key} is removed from semantic_dict")
        del semantic_dict[key]
    if debug:
        print("key comparison is done")


def generate_response(input_text):
    global result

    prompts = [
        {"role": "system", "content": "Task description: You are a triplet extractor! Your goal is to extract information about startup investments from articles, including the name of the startup, the amount of money invested, the names of the investors, the round of financing, and the date the investment took place. Your output should be a set of triplets in the form (subject, relation, object). If there is something not specified, write XXX instead."},
        {"role": "user", "content": "1. Example: Digital coaching platform CoachHub has secured new financing of approx. €25 million led by new investor Draper Esprit, alongside existing investors HV Capital, Partech, Speedinvest, signals Venture Capital and RTP Global. This latest round brings the total funds raised to over €40 million following the company’s +€16 million funding round in late 2019."},
        {"role": "assistant", "content": "\n(Coachhub, receives, €25 million)\n(Coachhub, receives, €16 million)\n(Coachhub, received in total, €40 million)\n(€16 million, was received in, 2019)\n(Draper Esprit, invests, €25 million)\n(HV Capital, invests, €25 million)\n(Partech, invests, €25 million)\n(Speedinvest, invests, €25 million)\n(signals Venture Capital, invests, €25 million)\n(RTP Global, invests, €25 million)"},
        {"role": "user", "content": "2. Example: The Munich-based startup Userlane just raised €4 million to finance its expansion and to further develop its product. Userlane, which was founded in 2015, offers a navigation system for software that allows users to understand and operate any application without formal training. The Series A investment round was led by Capnamic Ventures, and joined by High Tech Gründerfonds, main incubator, and FTR Ventures."},
        {"role": "assistant", "content": "\n(Userlane, receives, €4 million)\n(€4 million, roundofinvestment, Series A)\n(Capnamic Ventures, invests, €4 million)\n(High Tech Gründerfonds, invests, €4 million)\n(FTR Ventures, invests, €4 million)"},
        {"role": "user", "content": "3. Example: Igyxos has now raised €7.5 million in a Series A round led by Bpifrance through its Accelerate Biotechnologies Santé Fund, with participation from the Go Capital Amorçage II and Loire Valley Invest Funds managed by Go Capital and the Fonds Emergence Innovation II managed by Sofimac Innovation."},
        {"role": "assistant", "content": "\n(Igyxos, receives, €7.5 million)\n(€2.8 million, roundofinvestment, seed round)\n(Bpifrance, invests, €7.5 million)\n(Go Capital , invests, €7.5 million)\n(Sofimac Innovation, invests, €7.5 million)"},
        {"role": "user", "content": "4. Example: Today learning platform Masterplan.com has announced raising €13 million total funding, with existing investors only participating in the round. With the additional capital, Masterplan intends to further expand the development and distribution of its proprietary software."},
        {"role": "assistant", "content": "\n(Masterplan.com, receives, €13 million)\n(existing investors, invests, €13 million)"},
        {"role": "user", "content": "5. Example: Blacklane, the company that provides professional ground transportation at lowest rates around the globe, has added a mid-seven-digit round of funding at a valuation in the nine-figure Euro range from Japan-based Recruit Holdings Co., through its investment subsidiary RSP Fund No. 5, LLC."},
        {"role": "assistant", "content": "\n(Blacklane, receives, mid-seven-digit)\n(Blacklane, valuation at, nine-figure Euro range)\n(Recruit Holdings Co., invests, mid-seven-digit)"},
        {"role": "user", "content": "6. Example: Goodlord, one of the UK's leading property technology startups, has today announced the successful close of a Series B funding round. Following on from its 2017 €7 million Series A round, the business has now secured a further €7 million of funding, with the latest round led by new investor Finch Capital, supported by existing investors, Rocket Internet and angel investors."},
        {"role": "assistant", "content": "\n(Goodlord, receives, €7 million)\n(Goodlord, receives, €7 million)\n(€7 million, was received, today)\n(€7 million, was received, 2017)\n(€7 million, roundofinvestment, Series B)\n(€7 million, roundofinvestment, Series A)\n(Finch Capital, invests, €7 million)\n(Rocket Internet, invests, €7 million)\n(angel investors, invests, €7 million)"},
        {"role": "user", "content": "7. Example: The €1.86 million investment round consisted of a €1.15 million equity investment from Vendep Capital, a Northern European SaaS focused venture capital company, and a €751K loan from Business Finland."},
        {"role": "assistant", "content": "\n(Trustmary, received total, €1.86 million)\n(€1.86 million, has investment part, €1.15 million)\n(€1.86 million, has investment part, €751k)\n(Vendep Capital, invests part, €1.15 million)\n(Business Finland, invests part, €751k)"},
        {"role": "user", "content": f"Extract as shown and only with the relations as shown: the name of the startup, the amount of money invested, the names of the investors, the round of financing, and the date the investment took place. Your output should be a set of triplets in the form (subject, relation, object). If there is something not specified, write XXX instead. Article: {input_text}"},
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",  # gpt-3.5-turbo-0301 oder gpt-4-0314 oder gpt-4
        messages=prompts,
        temperature=0,

    )

    result = completion.choices[0]["message"]["content"]

    try:
        convert_chat_gpt_answer(input_text=input_text, output=result)
    except Exception as _:
        pass
    # make the current thread sleep for 4 seconds
    # TODO: time.sleep(((60 / 20) * len(prompts)) + 1)


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
        print("----------------------------------------------------------------")
        print("ai dict (gpt):", len(dict_ai_answers), dict_ai_answers)
        print("semantic dict (own):", len(dict_own_labels), dict_own_labels)
        print("----------------------------------------------------------------")
    comparison_of_results(answers_dict=dict_ai_answers, semantic_dict=dict_own_labels)
    format_converter(dict_own_labels, "self_results")
    format_converter(dict_ai_answers, "ai_results")
    print("code completed")

    if debug:
        print("Start of evaluation")
    import Text_Evaluation as txt_eval
    return txt_eval.evaluate()
