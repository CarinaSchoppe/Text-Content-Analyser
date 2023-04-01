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


def format_converter(semantic_dict, document):
    for text, value in semantic_dict.items():
        results = []
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
    valid = True
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
            valid = False
            print(f"because: answer from chat gpt was not in the right format, format: {output}")
            print(f"exact mistake: {answer}")
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
    dict_answers = {}
    prompt_results = []

    messages = [{"role": "user", "content": input_text}]

    prompts = [
        "Extract from this article the name of the startup, the amount of money invested, the names of the investors, the round of financing, the date the investment took place.\nFill in the following form:\nDate:\nStartup:\nInvestors:\nInvested amount:\nFinancing round:",
        "If there is something not specified, write XXX",
        "Please extract the relationship between two entities based on the given information, and represent it in the form of a triplet. The triplet should consist of a subject, a relationship, and an object. The subject represents the first entity, the relationship represents the connection between the two entities, and the object represents the second entity. Only use the relationships specified in the given examples and extract only the relevant triplets that pertain to the investment rounds in the startup scene."
        "Compare your triplets with these examples and adapt them: 1. Example: Digital coaching platform CoachHub has secured new financing of approx. €25 million led by new investor Draper Esprit, alongside existing investors HV Capital, Partech, Speedinvest, signals Venture Capital and RTP Global. This latest round brings the total funds raised to over €40 million following the company’s +€16 million funding round in late 2019.\n(Coachhub, receives, €25 million)\n(Coachhub, receives, €16 million)\n(Coachhub, received in total, €40 million)\n(€16 million, was received in, 2019)\n(Draper Esprit, invests, €25 million)\n(HV Capital, invests, €25 million)\n(Partech, invests, €25 million)\n(Speedinvest, invests, €25 million)\n(signals Venture Capital, invests, €25 million)\n(RTP Global, invests, €25 million) \n\n 2. Example: The Munich-based startup Userlane just raised €4 million to finance its expansion and to further develop its product. Userlane, which was founded in 2015, offers a navigation system for software that allows users to understand and operate any application without formal training. The Series A investment round was led by Capnamic Ventures, and joined by High Tech Gründerfonds, main incubator, and FTR Ventures.(Userlane, receives, €4 million)\n(€4 million, roundofinvestment, Series A)\n(Capnamic Ventures, invests, €4 million)\n(High Tech Gründerfonds, invests, €4 million)\n(FTR Ventures, invests, €4 million) \n\n 3. Example: Igyxos has now raised €7.5 million in a Series A round led by Bpifrance through its Accelerate Biotechnologies Santé Fund, with participation from the Go Capital Amorçage II and Loire Valley Invest Funds managed by Go Capital and the Fonds Emergence Innovation II managed by Sofimac Innovation.\n(Igyxos, receives, €7.5 million)\n(€2.8 million, roundofinvestment, seed round)\n(Bpifrance, invests, €7.5 million)\n(Go Capital , invests, €7.5 million)\n(Sofimac Innovation, invests, €7.5 million) \n\n 4. Example: Today learning platform Masterplan.com has announced raising €13 million total funding, with existing investors only participating in the round. With the additional capital, Masterplan intends to further expand the development and distribution of its proprietary software.\n(Masterplan.com, receives, €13 million)\n(existing investors, invests, €13 million) \n\n 5. Example: Blacklane, the company that provides professional ground transportation at lowest rates around the globe, has added a mid-seven-digit round of funding at a valuation in the nine-figure Euro range from Japan-based Recruit Holdings Co., through its investment subsidiary RSP Fund No. 5, LLC \n(Blacklane, receives, mid-seven-digit)\n(Blacklane, valuation at, nine-figure Euro range)\n(Recruit Holdings Co., invests, mid-seven-digit) \n\n 6. Example: Goodlord, one of the UK's leading property technology startups, has today announced the successful close of a Series B funding round. Following on from its 2017 €7 million Series A round, the business has now secured a further €7 million of funding, with the latest round led by new investor Finch Capital, supported by existing investors, Rocket Internet and angel investors\n(Goodlord, receives, €7 million)\n(Goodlord, receives, €7 million)\n(€7 million, was received, today)\n(€7 million, was received, 2017)\n(€7 million, roundofinvestment, Series B)\n(€7 million, roundofinvestment, Series A)\n(Finch Capital, invests, €7 million)\n(Rocket Internet, invests, €7 million)\n(angel investors, invests, €7 million) \n\n 7. Example: The €1.86 million investment round consisted of a €1.15 million equity investment from Vendep Capital, a Northern European SaaS focused venture capital company, and a €751K loan from Business Finland\n(Trustmary, received total, €1.86 million)\n(€1.86 million, has investment part, €1.15 million)\n(€1.86 million, has investment part, €751k)\n(Vendep Capital, invests part, €1.15 million)\n(Business Finland, invests part, €751k)",
        "Check your answers again with these general triplets and adapt them: \n(startup name, receives, amount of money)\n(amount of money, was received in, date)\n(amount of money, roundofinvestment, funding round)\n(startup name, received in total, amount of money)\n(amount of money, has investment part, amount of money)\n(investor name, invests part, amount of money)\n(investor name, invests, amount of money)\n(startup name, valuation at, amount of money)"
    ]
    prefix = ""

    for idx, prompt in enumerate(prompts):
        if idx == 0 and prefix is not None:
            prompt = prefix + prompt

        messages.append({"role": "system", "content": prompt})
        completion = openai.ChatCompletion.create(
            model="gpt-4",  # 3.5-turbo
            messages=messages,
        )

        result = completion.choices[0].message['content'].strip()
        prompt_results.append(result)

        # Das Ergebnis des letzten Prompts im dict_answers speichern
        if idx == len(prompts) - 1:
            dict_answers[prompt] = result

    # return prompt_results, dict_answers

    # completion = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[{"role": "user", "content": prefix + input_text}])
    # answer = completion.choices[0]["message"]["content"]
    convert_chat_gpt_answer(input_text=input_text, output=result)


def main():
    files = [filename for filename in os.listdir("../documents/xmi") if filename.endswith(".xmi")]
    for filename in files:
        extract_values_from_file(filename)
    if debug:
        print("extraction and conversion done")

    texts = {text for text in dict_entity.keys()}
    print("checiking_texts")
    print(texts)
    if debug:
        print("text extraction done")
    try:
        for file in os.listdir("../docs/results"):
            os.remove(os.path.join("../docs/results", file))
    except Exception as _:
        pass
    if debug:
        print("file deletion done")
    file_saver("triplets", "ai_results")
    file_saver("triplets", "self_results")
    if debug:
        print("file creation done")
    for text in texts:
        print(text)
        generate_response(input_text=text)
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
    # import Text_Evaluation as txt_eval
    # txt_eval.evalute()
    # ----------------------------------------------------------------------------------------------------------------#
    import re

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
    from tqdm import tqdm

    def evaluate():
        sns.set_theme()

        colors = ["#EBCCB7", "#C50F36"]
        custom_color_map = LinearSegmentedColormap.from_list(
            name='custom_cmap',
            colors=colors,
        )

        labels_df = pd.read_csv('../documents/results/self_results.csv', sep='\t')
        # labels_df = pd.read_csv('../documents/test_texts_NOGROUP.csv', sep='\t')
        labels_df = labels_df.dropna()
        labels = list()
        print(len(labels_df))

        for index, row in tqdm(labels_df.iterrows()):
            marker1, marker2, marker3 = '<triplet>', '<sub>', '<obj>'
            rp1 = marker1 + '.+?' + marker2
            rp2 = marker2 + '.+?' + marker3
            rp3 = marker3 + '.+?' + marker1
            head_ents = re.findall(rp1, row.triplets)
            tail_ents = re.findall(rp2, row.triplets)
            relations = re.findall(rp3, row.triplets)

            head_ents_clean = list()
            tail_ents_clean = list()
            relations_clean = list()

            for i in head_ents:
                result = re.search('<triplet>(.*)<sub>', i)
                head_ents_clean.append(result.group(1).strip())
            for i in tail_ents:
                result = re.search('<sub>(.*)<obj>', i)
                tail_ents_clean.append(result.group(1).strip())
            for i in relations:
                result = re.search('<obj>(.*)<triplet>', i)
                relations_clean.append(result.group(1).strip())

            len_str = len(row.triplets)
            if len(relations_clean) < len(head_ents_clean):
                work = row.triplets[len_str - 11:]
                last_rel = work.partition(">")[2]
                relations_clean.append(last_rel.strip())

            sample = list()
            for i in range(len(head_ents_clean)):
                entry = dict()
                entry['head'] = head_ents_clean[i]
                entry['type'] = relations_clean[i]
                entry['tail'] = tail_ents_clean[i]
                sample.append(entry)

            labels.append(sample)

        gold_cleaned = []
        for i in labels:
            entry = []
            for u in i:
                if not entry:
                    entry.append(u)
                elif u not in entry:
                    entry.append(u)

            gold_cleaned.append(entry)
        print("check1_goldcleaned")
        print(gold_cleaned)
        print("check2_end_gold")
        """could be interesting to see the recall for each relation type """
        rt = 'RECEIVES'
        gold_cleaned_rt = list()
        for i in gold_cleaned:
            sample = list()
            for u in i:
                if u['type'] == rt:
                    sample.append(u)
            gold_cleaned_rt.append(sample)

        predict_df = pd.read_csv('../documents/results/ai_results.csv', sep='\t')
        # labels_df = pd.read_csv('../documents/test_texts_NOGROUP.csv', sep='\t')
        predict_df = predict_df.dropna()
        predictions = list()
        print(len(predict_df))

        for index, row in tqdm(predict_df.iterrows()):
            marker1, marker2, marker3 = '<triplet>', '<sub>', '<obj>'
            rp1 = marker1 + '.+?' + marker2
            rp2 = marker2 + '.+?' + marker3
            rp3 = marker3 + '.+?' + marker1
            head_ents = re.findall(rp1, row.triplets)
            tail_ents = re.findall(rp2, row.triplets)
            preds = re.findall(rp3, row.triplets)

            head_ents_clean = list()
            tail_ents_clean = list()
            preds_clean = list()

            for i in head_ents:
                result = re.search('<triplet>(.*)<sub>', i)
                head_ents_clean.append(result.group(1).strip())
            for i in tail_ents:
                result = re.search('<sub>(.*)<obj>', i)
                tail_ents_clean.append(result.group(1).strip())
            for i in preds:
                result = re.search('<obj>(.*)<triplet>', i)
                preds_clean.append(result.group(1).strip())

            len_str = len(row.triplets)
            if len(preds_clean) < len(head_ents_clean):
                work = row.triplets[len_str - 11:]
                last_rel = work.partition(">")[2]
                preds_clean.append(last_rel.strip())

            sample = list()
            for i in range(len(head_ents_clean)):
                entry = dict()
                entry['head'] = head_ents_clean[i]
                entry['type'] = preds_clean[i]
                entry['tail'] = tail_ents_clean[i]
                sample.append(entry)

            predictions.append(sample)

        predictions_cleaned = []
        for i in predictions:
            entry = []
            for u in i:
                if not entry:
                    entry.append(u)
                elif u not in entry:
                    entry.append(u)

            predictions_cleaned.append(entry)
        print("check3_pred_clean")
        print(predictions_cleaned)
        print("check4_metrics")

        def calculate_metrics(tp, fp, rel):
            print(tp, fp, rel)
            precision = 100 * (len(tp) / (len(tp) + len(fp)))
            recall = 100 * (len(tp) / rel)
            if (precision + recall) == 0:
                f1score = None
            else:
                f1score = 2 * ((precision * recall) / (precision + recall))
            return precision, recall, f1score

        def tp_fp_fn_rel(approach, gold, pred):
            tp, fp, rel, fn = list(), list(), int(), list()

            """tp if whole triplet is correctly predicted"""
            if approach == 'triplet':
                # calculate tp and fp
                print(len(pred))
                print(len(gold))
                for i in enumerate(pred):
                    for u in i[1]:
                        if u in gold[i[0]]:
                            tp.append(u)
                        else:
                            fp.append(u)
                    for u in gold[i[0]]:
                        rel += 1
                        if u not in i[1]:
                            fn.append(u)

            """PROBLEM FOR ALL OF THEM"""
            """WE CANNOT COMPARE PER TRIPLET BUT PER ARTICLE"""
            """THEREFORE, ONLY SET-WISE COMPARISON MAKES SENSE"""

            """tp if head is correctly predicted"""
            if approach == 'head':
                # calculate tp and fp
                for i in enumerate(pred):
                    # calculate tp heads for each article

                    gold_heads = list()
                    for u in enumerate(gold[i[0]]):
                        gold_heads.append(u[1]['head'])
                    gold_heads = set(gold_heads)

                    preds_sample = list()
                    for u in i[1]:
                        preds_sample.append(u['head'])
                    preds_sample = set(preds_sample)

                    # check for each article if prediction heads occur in gold heads
                    for u in preds_sample:
                        if u in gold_heads:
                            tp.append(u)
                        else:
                            fp.append(u)

                    for u in gold_heads:
                        rel += 1
                        if u not in preds_sample:
                            fn.append(u)

            """tp if tail is correctly predicted"""
            if approach == 'tail':
                # calculate tp and fp
                for i in enumerate(pred):
                    # calculate tp heads for each article

                    gold_tails = list()
                    for u in enumerate(gold[i[0]]):
                        gold_tails.append(u[1]['tail'])
                    gold_tails = set(gold_tails)

                    preds_sample = list()
                    for u in i[1]:
                        preds_sample.append(u['tail'])
                    preds_sample = set(preds_sample)

                    # check for each article if prediction heads occur in gold heads
                    for u in preds_sample:
                        if u in gold_tails:
                            tp.append(u)
                        else:
                            fp.append(u)

                    for u in gold_tails:
                        rel += 1
                        if u not in preds_sample:
                            fn.append(u)

            """tp if relation is correctly predicted"""
            if approach == 'relation':
                # calculate tp and fp
                for i in enumerate(pred):
                    # calculate tp heads for each article

                    gold_types = list()
                    for u in enumerate(gold[i[0]]):
                        gold_types.append(u[1]['type'])
                    gold_types = set(gold_types)

                    preds_sample = list()
                    for u in i[1]:
                        preds_sample.append(u['type'])
                    preds_sample = set(preds_sample)

                    # check for each article if prediction heads occur in gold heads
                    for u in preds_sample:
                        if u in gold_types:
                            tp.append(u)
                        else:
                            fp.append(u)

                    for u in gold_types:
                        rel += 1
                        if u not in preds_sample:
                            fn.append(u)

            return tp, fp, fn, rel

        def confusion_matrix(tp, fp, fn, title, tn=0):
            # sns.set(font_scale=2)
            # cm = np.array([[len(tp), len(fp)], [len(fn), tn]])
            # classes = ['true triplets', 'false triplets']
            #
            # fig, axs = plt.subplots()
            # plt.subplots_adjust(left=0.2, bottom=0.2)
            #
            # hm = sns.heatmap(cm, cmap = custom_color_map, annot=True, xticklabels=classes, yticklabels=classes, cbar=False, fmt="d",ax = axs)
            # hm.set(title=title, xlabel="predicted label", ylabel="true label")
            # sns.set_theme(rc = {'figure.figsize':(10,7)})
            # precision, recall, f1score = calculate_metrics(tp, fp, rel)
            #
            # table = plt.table(cellText=[[round(precision, 1)], [round(recall, 1)], [round(f1score, 1)]],
            #                 rowLabels=['Precision', 'Recall', 'F1-Score'],
            #                 colLabels=['Value [%]'],
            #                 bbox = ([0.3, -0.6, 0.5, 0.3]))
            #
            # fig.savefig('test.svg')
            # plt.show()

            sns.set(font_scale=2)
            cm = np.array([[len(tp), len(fn)], [len(fp), tn]])
            classes = ['true triplets', 'false triplets']

            fig, ax = plt.subplots(figsize=(10, 6))
            ax = sns.heatmap(cm, cmap=custom_color_map, annot=True, xticklabels=classes, yticklabels=classes, cbar=False, fmt="d")
            ax.set(title=title, xlabel="predicted label", ylabel="true label")
            fig.savefig('Result.svg')

        tp, fp, fn, rel = tp_fp_fn_rel('triplet', gold_cleaned, predictions_cleaned)  # TODO: hier change that!

        precision, recall, f1score = calculate_metrics(tp, fp, rel)

        # title = "confusion matrix for predictions on text"
        confusion_matrix(tp, fp, fn, title=None)

        print('METRICS')
        print('-------------------------')
        print('Precision: ', round(precision, 2), '%')
        print('Recall: ', round(recall, 2), '%')
        if f1score != None:
            print('F1-Score: ', round(f1score, 2), '%')

        def error_analysis(approach, gold, pred):
            tp, fp, rel, fn, index_fp, index_fn = list(), list(), int(), list(), list(), list()

            """tp if whole triplet is correctly predicted"""
            if approach == 'triplet':
                # calculate tp and fp
                for i in enumerate(pred):
                    for u in i[1]:
                        if u in gold[i[0]]:
                            tp.append(u)
                        else:
                            fp.append(u)
                            index_fp.append(i[0])

                    for u in gold[i[0]]:
                        rel += 1
                        if u not in i[1]:
                            fn.append(u)
                            index_fn.append(i[0])

            return fp, index_fp, fn, index_fn

        fp_e, index_fp, fn_e, index_fn = error_analysis('triplet', gold_cleaned, predictions_cleaned)  # change that!

        new_list = [index_fp, fp_e, index_fn, fn_e]
        df = pd.DataFrame(new_list)

        writer = pd.ExcelWriter('errors.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='errors_raw', index=False)
        writer.save()

    evaluate()


if __name__ == "__main__":
    main()
