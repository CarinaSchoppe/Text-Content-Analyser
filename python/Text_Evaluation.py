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

    print(gold_cleaned)

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

    print(predictions_cleaned)

    def calculate_metrics(tp, fp, rel):
        if len(tp) + len(fp) == 0:
            precision = None
        else:
            precision = round(100 * (len(tp) / (len(tp) + len(fp))), 2)
        if rel == 0:
            recall = None
        else:
            recall = round(100 * (len(tp) / rel), 2)
        if precision is None or recall is None:
            f1score = None
        elif (precision + recall) == 0:
            f1score = None
        else:
            f1score = round(2 * ((precision * recall) / (precision + recall)), 2)
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

        """PROBLEM FOR ALL OF THEM
        WE CANNOT COMPARE PER TRIPLET BUT PER ARTICLE
        THEREFORE, ONLY SET-WISE COMPARISON MAKES SENSE

        tp if head is correctly predicted"""
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

        sns.set(font_scale=2)
        cm = np.array([[len(tp), len(fn)], [len(fp), tn]])
        classes = ['true triplets', 'false triplets']

        fig, ax = plt.subplots(figsize=(10, 8))
        ax = sns.heatmap(cm, cmap=custom_color_map, annot=True, xticklabels=classes, yticklabels=classes, cbar=False, fmt="d")
        ax.set(title=title, xlabel="predicted label", ylabel="true label")
        # fig.savefig('Result.svg')
        return fig

    tp, fp, fn, rel = tp_fp_fn_rel('triplet', gold_cleaned, predictions_cleaned)  # TODO: hier change that!

    precision, recall, f1score = calculate_metrics(tp, fp, rel)

    grafics = confusion_matrix(tp, fp, fn, title=None)

    precision = round(precision, 2) if precision is not None else 'N/A'
    recall = round(recall, 2) if recall is not None else 'N/A'
    f1_score = f1score
    print('\n-------------------------')
    print('METRICS')
    print('Precision: ', precision, '%' if precision is not None else '')
    print('Recall: ', recall, '%' if recall is not None else '')
    if f1score is None:
        print('F1-Score: N/A')
    else:
        print(f'F1-Score: {f1score}%')
    print('-------------------------\n')

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

    # save as excel
    # df.to_excel('errors.xlsx', sheet_name='errors_raw', index=False, engine='xlsxwriter')

    return grafics, precision, recall, f1_score
