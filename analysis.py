import datetime
import math
import re

import numpy as np
import pandas as pd
import matplotlib as mpl
import pymorphy2
import matplotlib.dates as mdates

morph = pymorphy2.MorphAnalyzer()
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings(action='once')

large = 22
med = 16
small = 12
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


def do_word_count_analysis_pie(comments, phrases, is_order_matter=True, start_date=None, end_date=None):
    '''

    :param comments: список комментариев
    :param phrases: список фраз
    :param is_order_matter: учитывать ли порядок слов в фразах
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :return: имя файла с графиком
    '''
    if start_date is None:
        start_date = datetime.date(9999, 1, 1)
        for comment in comments:
            if comment.date < start_date:
                start_date = comment.date
    if end_date is None:
        end_date = datetime.date(1, 1, 1)
        for comment in comments:
            if comment.date > end_date:
                end_date = comment.date

    equal_phrase_counts = get_equal_phases_counts(comments, phrases, is_order_matter, start_date, end_date)
    return save_pie(equal_phrase_counts, phrases)


def get_equal_phases_counts(comments, phrases, is_order_matter, start_date, end_date):
    date_comments = []
    for comment in comments:
        if (comment.date <= end_date) and (comment.date >= start_date):
            date_comments.append(comment)

    normal_phrases = get_normal_phrases(phrases)

    equal_word_counts = [0 for i in range(len(normal_phrases))]
    equal_phrase_counts = [0 for i in range(len(normal_phrases))]

    if is_order_matter:
        for comment in date_comments:
            for word in re.findall(r'\w+', comment.text):
                normal_word = morph.parse(word)[0].normal_form
                for i in range(len(normal_phrases)):
                    if equal_word_counts[i] < len(normal_phrases[i]):
                        if normal_phrases[i][equal_word_counts[i]] == normal_word:
                            equal_word_counts[i] += 1
                            if equal_word_counts[i] == len(normal_phrases[i]):
                                #equal_word_counts[i] = 0  #разкоментировать для учитывания повторений в одном комменте
                                equal_phrase_counts[i] += 1

                        else:
                            equal_word_counts[i] = 0
            for j in range(len(equal_word_counts)):
                equal_word_counts[j] = 0
    else:
        for comment in date_comments:
            words = re.findall(r'\w+', comment.text)
            for i in range(len(words)):
                words[i] = morph.parse(words[i])[0].normal_form
            for i in range(len(normal_phrases)):
                for phrase_word in normal_phrases[i]:
                    for word in words:
                        if word == phrase_word:
                            equal_word_counts[i] += 1
                            break
                if equal_word_counts[i] == len(normal_phrases[i]):

                    equal_phrase_counts[i] += 1

                equal_word_counts[i] = 0

    return equal_phrase_counts


def get_normal_phrases(phrases):
    normal_phrases = []
    for phrase in phrases:
        sub_words = []
        for sub_word in re.findall(r'\w+', phrase):
            sub_words.append(morph.parse(sub_word)[0].normal_form)
        normal_phrases.append(sub_words)

    return normal_phrases


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

    plt.style.use('seaborn-whitegrid')
    plt.pie(x=counts_without_null, labels=phrases_without_null, autopct=lambda pct: func(pct, counts), rotatelabels=True)
    plt.title("Диаграма частотности встречи фраз")
    plt.ylabel("")
    plt.legend(title="Фразы",
               loc="upper left",
               bbox_to_anchor=(1, 0.6),
               edgecolor='r')

    # plt.savefig(png_name, dpi=200)
    plt.show()
    return png_name


def do_word_count_analysis_hist(comments, phrases, day_week_month='day', is_order_matter=True, start_date=None, end_date=None):
    '''

    :param comments: список комментариев
    :param phrases: список фраз
    :param day_week_month: 'day' или 'week' или 'month' (определяет на какие промежутки будет разбит интервал)
    :param is_order_matter: учитывать ли порядок слов в фразах
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :return: имя файла с графиком
    '''

    if start_date is None:
        start_date = datetime.date(9999,1,1)
        for comment in comments:
            if comment.date < start_date:
                start_date = comment.date
    if end_date is None:
        end_date = datetime.date(1,1,1)
        for comment in comments:
            if comment.date > end_date:
                end_date = comment.date

    dates = get_equal_phases_counts_with_date_by_date(comments, phrases, day_week_month, start_date, end_date, is_order_matter)
    return save_histogram(dates, phrases, day_week_month)


def get_equal_phases_counts_with_date_by_date(comments, phrases, day_week_month, start_date, end_date, is_order_matter):
    date_comments = []
    for comment in comments:
        if (comment.date <= end_date) and (comment.date >= start_date):
            date_comments.append(comment)

    normal_phrases = get_normal_phrases(phrases)

    equal_word_counts = [0 for i in range(len(normal_phrases))]
    if day_week_month == 'day':
        interval = (end_date - start_date).days
    elif day_week_month == 'week':
        interval = math.ceil((end_date - start_date).days / 7) + 1
    elif day_week_month == 'month':
        interval = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    else:
        raise NotImplementedError
    counts = []
    for i in range(len(phrases)):
        counts.append([0 for j in range(interval)])

    if is_order_matter:
        for comment in date_comments:
            for word in re.findall(r'\w+', comment.text):
                normal_word = morph.parse(word)[0].normal_form
                for i in range(len(normal_phrases)):
                    if equal_word_counts[i] < len(normal_phrases[i]):
                        if normal_phrases[i][equal_word_counts[i]] == normal_word:
                            equal_word_counts[i] += 1
                            if equal_word_counts[i] == len(normal_phrases[i]):

                                #equal_word_counts[i] = 0 #разкомментировать для учета повторений в одном комменте
                                if day_week_month == 'day':
                                    counts[i][(comment.date - start_date).days] += 1
                                elif day_week_month == 'week':
                                    counts[i][math.ceil((comment.date - start_date).days / 7)] += 1
                                elif day_week_month == 'month':
                                    counts[i][(comment.date.year - start_date.year) * 12 + (comment.date.month - start_date.month)] += 1

                        else:
                            equal_word_counts[i] = 0
            for j in range(len(equal_word_counts)):
                equal_word_counts[j] = 0
    else:
        for comment in date_comments:
            words = re.findall(r'\w+', comment.text)
            for i in range(len(words)):
                words[i] = morph.parse(words[i])[0].normal_form
            for i in range(len(normal_phrases)):
                for phrase_word in normal_phrases[i]:
                    for word in words:
                        if word == phrase_word:
                            equal_word_counts[i] += 1
                            break
                if equal_word_counts[i] == len(normal_phrases[i]):

                    if day_week_month == 'day':
                        counts[i][(comment.date - start_date).days] += 1
                    elif day_week_month == 'week':
                        counts[i][math.ceil((comment.date - start_date).days / 7)] += 1
                    elif day_week_month == 'month':
                        counts[i][
                            (comment.date.year - start_date.year) * 12 + (comment.date.month - start_date.month)] += 1

                equal_word_counts[i] = 0

    dates = [0 for j in range(interval)]
    for i in range(len(dates)):
        if day_week_month == 'day':
            dates[i] = (start_date + datetime.timedelta(days=i))
        elif day_week_month == 'week':
            dates[i] = (start_date + datetime.timedelta(days=i*7))
        elif day_week_month == 'month':
            dates[i] = datetime.date(start_date.year + (start_date.month + i - 1)//12, (start_date.month + i - 1)%12 + 1, 15)

    return [dates, counts]


def save_histogram(counts, phrases, day_week_month):
    png_name = 'graph.png'
    plt.style.use('bmh')

    fig, ax = plt.subplots()

    if (day_week_month == 'day') or (day_week_month == 'week'):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    elif day_week_month == 'month':
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    for sub_counts in counts[1]:
        ax.plot(counts[0], sub_counts)

    ax.set_title("График частотности встречи фраз")
    plt.legend(title="Фразы", labels=phrases)

    plt.show()

    return png_name
