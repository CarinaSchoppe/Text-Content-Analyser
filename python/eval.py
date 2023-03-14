import re

import pandas as pd
import seaborn as sns;
from tqdm import tqdm

sns.set_theme()
from matplotlib.colors import LinearSegmentedColormap

colors = ["#EBCCB7", "#C50F36"]
custom_color_map = LinearSegmentedColormap.from_list(
    name='custom_cmap',
    colors=colors)
# Section to generate labels
labels_df = pd.read_csv('test_texts_NOGROUP.csv', sep='\t')
labels_df = labels_df.dropna()
labels = list()

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
