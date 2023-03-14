import re

import openai

openai.api_key = "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"


def generate_response(input_text, prefix=""):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prefix + input_text}]
    )
    return completion.choices[0]["message"]["content"]


dict_answers = dict()


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
