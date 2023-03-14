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


def convert_chat_gpt_answer(input: str, output: str):
    # answer format = (Ent; relation; entity)
    # convert into differeent variables
    answers = output.split("\n")
    for answer in answers:
        try:

            answer = re.sub(r"[\(\)]", "", answer)
            answer = answer.split(",")

            entity = answer[0]
            relation = answer[1][1:]
            second_entity = answer[2][1:]

            if (input in dict_answers):
                # get the len of elements in the dict_answers[input] and add 1 to it
                dict_answers[input][len(dict_answers[input])] = (entity, relation, second_entity)
            else:
                input_dict = dict()
                input_dict[0] = (entity, relation, second_entity)
                dict_answers[input] = input_dict
        except Exception as exception:
            print(exception)


def file_saver(text, document):
    with open(f"../documents/results/{document}.csv", "a", encoding="UTF-8") as file:
        file.write(text + "\n")


def generate_response(input_text, prefix=f"""Act like a data engineer. You need to extract relationships in the form of triplets from articles that deal with investment rounds in the start-up scene. I will give you some examples so you know what to extract. Do you understand?

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
    print(f"AI ANSWER: {answer}")
    convert_chat_gpt_answer(input=input_text, output=answer)


def main():
    files = [filename for filename in os.listdir("../documents/xmi") if filename.endswith(".xmi")]
    for filename in files:
        extract_values_from_file(filename)
    print("extraction and conversion done")
    texts = {text for text in dict_entity.keys()}
    print("text extraction done")
    # delete the files in f"../documents/results"
    try:
        for file in os.listdir("../documents/results"):
            os.remove(os.path.join("../documents/results", file))
    except Exception as _:
        pass
    print("file deletion done")

    file_saver("triplets", "ai_results")
    file_saver("triplets", "self_results")
    print("file creation done")
    # for text in texts:
    # generate_response(text)
    convert_chat_gpt_answer(
        """BOOKR Kids, a reading-based early learning ‘edu-tainment’ company has disclosed €2 million in new funding and a further €2 million in convertible note. The round is led by Bonitas, a private VC owned by billionaire Sándor Csányi. BOOKR Kids will use the financing to take their English-learning literacy programme BOOKR Class to the global education market, and boost further the company goal of mitigating COVID-19’s impact on education. The past year has been a turning point for BOOKR Kids, as much as for other edtech players. The importance of digital educational materials has increased enormously, so the company, creating interactive animated story books with educational games, did not stop for a moment. BOOKR Class has also been recognized during school closure as an official textbook in Hungary and is now used by 100K Hungarian students. With the help of this investment, BOOKR Kids will develop more innovative content and a more comprehensive curriculum, including 21st-century skills. To facilitate language acquisition, BOOKR Kids’ animated interactive e-books and apps follow a researched methodology. The texts and activities are designed to support individual and classroom use as well. The illustrations and animations support the understanding of the texts, but they are moderate enough not to distract users from reading. Moreover, the entertaining educational games help to highlight the main linguistic elements and features for a more focused, intentional learning and practice. Besides literacy, the format itself will address 21st-century skills as well such as creativity, communication, collaboration and critical thinking.""", """(BOOKR Kids, disclosed, €2 million)
(BOOKR Kids, disclosed, €2 million in convertible note)
(Bonitas, leads round, BOOKR Kids)
(Bonitas, is owned by, Sándor Csányi)
(BOOKR Kids, will use financing, take BOOKR Class to global education market)
(BOOKR Kids, will use financing, boost company goal of mitigating COVID-19’s impact on education)
(BOOKR Class, recognized as official textbook, Hungary)
(BOOKR Class, used by, 100K Hungarian students)
(BOOKR Kids, will develop, more innovative content)
(BOOKR Kids, will develop, more comprehensive curriculum)
(BOOKR Kids' e-books and apps, follow, researched methodology)
(e-books and apps, designed to support, individual and classroom use)
(illustrations and animations, support, understanding of texts)
(entertaining educational games, help to highlight, linguistic elements and features)
(format, will address, 21st-century skills)
(format, will address, creativity, communication, collaboration, and critical thinking)""")
    print("ai answers done")
    format_converter(dict_semantic, "self_results")
    format_converter(dict_answers, "ai_results")


if __name__ == "__main__":
    main()