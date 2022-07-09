import datetime
import math
import re
from datetime import date

import numpy as np
import pandas as pd
import pymorphy2
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())

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
          'legend.title_fontsize': large,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")


def get_comments_in_date(comments, start_date, end_date):
    date_comments = []
    for comment in comments:
        if (comment.date <= end_date) and (comment.date >= start_date):
            date_comments.append(comment)

    return date_comments


def get_interval(day_week_month, start_date, end_date):
    if day_week_month == 'day':
        interval = (end_date - start_date).days + 1
    elif day_week_month == 'week':
        interval = math.ceil(((end_date - start_date).days + 1) / 7)
    elif day_week_month == 'month':
        interval = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month + 1)
    else:
        raise NotImplementedError

    return interval


def do_word_count_analysis_pie(comments, phrases, is_order_matter=True, start_date=None, end_date=None):
    '''
    Строит круговую диаграмму по кколичеству встреченных фраз
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
    date_comments = get_comments_in_date(comments, start_date, end_date)

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
    plt.style.use('seaborn-whitegrid')

    phrases_without_null = []
    for i in range(len(counts)):
        if counts[i] != 0:
            phrases_without_null.append(phrases[i])
        else:
            phrases_without_null.append('')

    def func(pct, all_vals):
        if pct != 0:
            absolute = int(np.round(pct / 100. * np.sum(all_vals)))
            return "{:.1f}% ({:d})".format(pct, absolute)
        else:
            return ''

    plt.style.use('seaborn-whitegrid')
    plt.pie(x=counts, labels=phrases_without_null, rotatelabels=True, autopct=lambda pct: func(pct, counts))
    plt.title("Диаграма частотности фраз")

    plt.legend(phrases,
               title="Фразы",
               loc="upper left",
               bbox_to_anchor=(1, 0.6),
               edgecolor='r')

    plt.savefig(png_name, dpi=200)
    #plt.show()

    return png_name


def do_word_count_analysis_hist(comments, phrases, day_week_month='day', is_order_matter=True, start_date=None, end_date=None):
    '''
    Строит график количества встреченных фраз по датам
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
    date_comments = get_comments_in_date(comments, start_date, end_date)

    normal_phrases = get_normal_phrases(phrases)

    equal_word_counts = [0 for i in range(len(normal_phrases))]
    interval = get_interval(day_week_month, start_date, end_date)
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
                        counts[i][math.ceil(((comment.date - start_date).days + 1) / 7) - 1] += 1
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

    ax.set_title("График частотности фраз")
    plt.legend(title="Фразы", labels=phrases)

    #plt.show()
    plt.savefig(png_name, dpi=200)

    return png_name


def do_sentiment_analysis(comments, day_week_month='day', start_date=None, end_date=None):
    '''
    Строит гистограмму тональности комментариев по датам
    :param comments: список комментариев
    :param day_week_month: 'day' или 'week' или 'month' (определяет на какие промежутки будет разбит интервал )
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :return: имя файла гистограммы
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

    date_comments = get_comments_in_date(comments, start_date, end_date)

    sentiments = get_sentiment_predicts(date_comments)

    moods = []
    for result in sentiments:
        for key in result.keys():
            if key == 'positive':
                moods.append(0)
            elif key == 'negative':
                moods.append(1)
            elif key == 'neutral':
                moods.append(2)

    dates = []
    for comment in date_comments:
        dates.append(comment.date)

    dates_with_counts = get_dates_with_counts(dates, moods, day_week_month, start_date, end_date)

    return save_sentiment_hist(dates_with_counts[0], dates_with_counts[1], day_week_month)


def get_sentiment_predicts(comments):
    texts = []
    for comment in comments:
        texts.append(comment.text)
    return model.predict(texts, k=1)


def get_dates_with_counts(dates, moods, day_week_month, start_date, end_date):
    interval = get_interval(day_week_month, start_date, end_date)

    counts = []
    for j in range(3):
        counts.append([0 for i in range(interval)])

    for i in range(len(moods)):
        if day_week_month == 'day':
            counts[moods[i]][(dates[i] - start_date).days] += 1
        elif day_week_month == 'week':
            counts[moods[i]][math.ceil(((dates[i] - start_date).days+1) / 7) - 1] += 1
        elif day_week_month == 'month':
            counts[moods[i]][(dates[i].year - start_date.year) * 12 + (dates[i].month - start_date.month)] += 1

    result_dates = [0 for j in range(interval)]
    for i in range(len(result_dates)):
        if day_week_month == 'day':
            result_dates[i] = (start_date + datetime.timedelta(days=i))
        elif day_week_month == 'week':
            result_dates[i] = (start_date + datetime.timedelta(days=i * 7))
        elif day_week_month == 'month':
            result_dates[i] = datetime.date(start_date.year + (start_date.month + i - 1) // 12,
                                     (start_date.month + i - 1) % 12 + 1, 15)

    return [result_dates, counts]


def save_sentiment_hist(dates, counts, day_week_month):
    png_name = 'graph.png'
    plt.style.use('bmh')

    fig, ax = plt.subplots()

    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    width = 0.25
    r = np.arange(len(dates))

    plt.bar(r, counts[0], width=width, label='позитивные', color='lime')
    plt.bar(r + width, counts[1], width=width, label='негативные', color='red')
    plt.bar(r + 2*width, counts[2], width=width, label='нейтральные', color='tan')

    str_dates = []
    if (day_week_month == 'day') or (day_week_month == 'week'):
        for i in range(len(dates)):
            if i%math.ceil(len(dates)/25) == 0:
                str_dates.append(dates[i].strftime("%d-%m-%Y"))
            else:
                str_dates.append('')
    else:
        for l_date in dates:
            str_dates.append(l_date.strftime("%m-%Y"))

    plt.xticks(r + width/2, str_dates)

    plt.title = "График тональности комментариев"
    plt.legend(title="Окрас")

    #plt.show()
    plt.savefig(png_name, dpi=200)

    return png_name
