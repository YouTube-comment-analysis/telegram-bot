import datetime
import re

import numpy as np
import pymorphy2
from matplotlib import pyplot as plt

from analysis import auxiliary
from comment import Comment

morph = pymorphy2.MorphAnalyzer()
auxiliary.set_plt_params(plt)


def make_word_count_analysis_pie(comments: list[Comment], phrases: list[str], is_order_matter=True, start_date=None, end_date=None, image_name='pie') -> str:
    """
    Строит круговую диаграмму по количеству встреченных фраз
    :param comments: список комментариев
    :param phrases: список фраз
    :param is_order_matter: учитывать ли порядок слов в фразах
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :param image_name: имя файла (использовать телеграм id)
    :return: относительный путь к круговой диаграмме
    """
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
    return save_pie(equal_phrase_counts, phrases, image_name)


def get_equal_phases_counts(comments: list[Comment], phrases: list[str], is_order_matter: bool, start_date: datetime.date, end_date: datetime.date) -> list[int]:
    date_comments = auxiliary.get_comments_in_date(comments, start_date, end_date)

    normal_phrases = auxiliary.get_normal_phrases(phrases)

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


def save_pie(counts: list[int], phrases: list[str], image_name: str):
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

    path = r'photos/' + image_name + '.png'
    plt.savefig(path, dpi=200)
    plt.clf()
    #plt.show()

    return path
