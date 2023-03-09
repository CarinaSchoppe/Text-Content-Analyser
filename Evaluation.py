import openai


def generate_response(input_text, prefix=""):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prefix + input_text}]
    )
    print(completion)
    return completion.choices[0]["text"]


gold_answers = dict()


def extract_values_from_file(filepath):
    pass


def evaluate(gold_answers, ai_answers):
    pass
