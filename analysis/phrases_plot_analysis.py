import datetime
import math
import re

import pymorphy2
from matplotlib import pyplot as plt
from analysis import auxiliary
import matplotlib.dates as mdates
from comment import Comment


morph = pymorphy2.MorphAnalyzer()
auxiliary.set_plt_params(plt)


def make_word_count_analysis_plot(comments: list[Comment], phrases: list[str], grouping: auxiliary.GroupingType, is_order_matter=True, start_date=None, end_date=None, image_name='hist') -> str:
    """
    Строит график количества встреченных фраз по датам

    :param comments: список комментариев
    :param phrases: список фраз
    :param grouping: 'day' или 'week' или 'month' (определяет на какие промежутки будет разбит интервал)
    :param is_order_matter: учитывать ли порядок слов в фразах
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :param image_name: имя файла (использовать телеграм id)
    :return: относительный путь к диаграмме
    """

    if start_date is None:
        start_date = auxiliary.get_earliest_comment_date(comments)
    if end_date is None:
        end_date = auxiliary.get_latest_comment_date(comments)

    pair = get_equal_phases_counts_with_date_by_date(comments, phrases, grouping, start_date, end_date, is_order_matter)
    return save_histogram(pair['dates'], pair['counts'], phrases, grouping, image_name)


def get_equal_phases_counts_with_date_by_date(comments: list[Comment], phrases: list[str], grouping: auxiliary.GroupingType, start_date: datetime.date, end_date: datetime.date, is_order_matter: bool) -> dict:
    date_comments = auxiliary.get_comments_in_date(comments, start_date, end_date)

    normal_phrases = auxiliary.get_normal_phrases(phrases)

    equal_word_counts = [0 for i in range(len(normal_phrases))]
    interval = auxiliary.get_interval_len(grouping, start_date, end_date)
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
                                if grouping == auxiliary.GroupingType.day:
                                    counts[i][(comment.date - start_date).days] += 1
                                elif grouping == auxiliary.GroupingType.week:
                                    counts[i][math.ceil((comment.date - start_date).days / 7)] += 1
                                elif grouping == auxiliary.GroupingType.month:
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

                    if grouping == auxiliary.GroupingType.day:
                        counts[i][(comment.date - start_date).days] += 1
                    elif grouping == auxiliary.GroupingType.week:
                        counts[i][math.ceil(((comment.date - start_date).days + 1) / 7) - 1] += 1
                    elif grouping == auxiliary.GroupingType.month:
                        counts[i][
                            (comment.date.year - start_date.year) * 12 + (comment.date.month - start_date.month)] += 1

                equal_word_counts[i] = 0

    dates = [0 for j in range(interval)]
    for i in range(len(dates)):
        if grouping == auxiliary.GroupingType.day:
            dates[i] = (start_date + datetime.timedelta(days=i))
        elif grouping == auxiliary.GroupingType.week:
            dates[i] = (start_date + datetime.timedelta(days=i*7))
        elif grouping == auxiliary.GroupingType.month:
            dates[i] = datetime.date(start_date.year + (start_date.month + i - 1)//12, (start_date.month + i - 1) % 12 + 1, 15)

    return {'dates': dates, 'counts': counts}


def save_histogram(dates: list[datetime.date], counts: list[int], phrases: list[str], grouping: auxiliary.GroupingType, image_name: str) -> str:
    plt.style.use('bmh')

    fig, ax = plt.subplots()

    if (grouping == auxiliary.GroupingType.day) or (grouping == auxiliary.GroupingType.week):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    elif grouping == auxiliary.GroupingType.month:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    for sub_counts in counts:
        ax.plot(dates, sub_counts)

    ax.set_title("График частотности фраз")
    plt.legend(title="Фразы", labels=phrases)

    #plt.show()
    path = r'photos/' + image_name + '.png'
    plt.savefig(path, dpi=200)
    plt.clf()

    return path
