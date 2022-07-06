import re

import numpy as np
import pandas as pd
import matplotlib as mpl
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings(action='once')

large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")


def do_words_count_analysis(comments, phrases):
    equal_phrase_counts = get_equal_phases_counts(comments, phrases)
    return save_pie(equal_phrase_counts, phrases)


def get_equal_phases_counts(comments, phrases):
    normal_words = []
    for phrase in phrases:
        sub_words = []
        for sub_word in re.findall(r'\w+', phrase):
            sub_words.append(morph.parse(sub_word)[0].normal_form)
        normal_words.append(sub_words)

    equal_word_counts = [0 for i in range(len(normal_words))]
    equal_phrase_counts = [0 for i in range(len(normal_words))]

    for comment in comments:
        for word in re.findall(r'\w+', comment.text):
            normal_word = morph.parse(word)[0].normal_form
            for i in range(len(normal_words)):
                if normal_words[i][equal_word_counts[i]] == normal_word:
                    equal_word_counts[i] += 1
                    if equal_word_counts[i] == len(normal_words[i]):
                        equal_word_counts[i] = 0
                        equal_phrase_counts[i] += 1
                else:
                    equal_word_counts[i] = 0

    return equal_phrase_counts


def save_pie(counts, phrases):
    png_name = 'graph.png'
    counts_without_null = []
    phrases_without_null = []
    for i in range(len(counts)):
        if counts[i] != 0:
            counts_without_null.append(counts[i])
            phrases_without_null.append(phrases[i])

    def func(pct, allvals):
        absolute = int(np.round(pct / 100. * np.sum(allvals)))
        return "{:.1f}% ({:d})".format(pct, absolute)

    plt.pie(x=counts_without_null, labels=phrases_without_null, autopct=lambda pct: func(pct, counts), rotatelabels=True)
    plt.title("Количества слов")
    plt.ylabel("")
    plt.savefig(png_name, dpi=200)

    return png_name



#print_circle(['one','two','tree','four'])