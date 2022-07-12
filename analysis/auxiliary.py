import datetime
import enum
import math
import re

import matplotlib
import pymorphy2

from comment import Comment

morph = pymorphy2.MorphAnalyzer()


class GroupingType(enum.Enum):
    day = 'day'
    week = 'week'
    month = 'month'


def set_plt_params(matplotlib_pyplot):
    large = 22
    med = 16
    small = 12
    params = {'legend.fontsize': med,
              'legend.title_fontsize': large,
              'figure.figsize': (16, 10),
              'axes.labelsize': med,
              'axes.titlesize': med,
              'xtick.labelsize': med,
              'ytick.labelsize': med,
              'figure.titlesize': large}
    matplotlib_pyplot.rcParams.update(params)
    matplotlib_pyplot.style.use('seaborn-whitegrid')
    #sns.set_style("white")


def get_comments_in_date(comments: list[Comment], start_date: datetime.date, end_date: datetime.date) -> list[Comment]:
    date_comments = []
    for comment in comments:
        if (comment.date <= end_date) and (comment.date >= start_date):
            date_comments.append(comment)

    return date_comments


def get_interval_len(grouping: GroupingType, start_date: datetime.date, end_date: datetime.date) -> int:
    if grouping == GroupingType.day:
        interval = (end_date - start_date).days + 1
    elif grouping == GroupingType.week:
        interval = math.ceil(((end_date - start_date).days + 1) / 7)
    elif grouping == GroupingType.month:
        interval = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month + 1)
    else:
        raise NotImplementedError

    return interval


def get_normal_phrases(phrases: list[str]) -> list[list[str]]:
    """
    Возвращает массив фраз, поделённоых на нормализованные слова

    :param phrases: Необработанный список фраз
    :return:
    """
    normal_phrases = []
    for phrase in phrases:
        sub_words = []
        for sub_word in re.findall(r'\w+', phrase):
            sub_words.append(morph.parse(sub_word)[0].normal_form)
        normal_phrases.append(sub_words)

    return normal_phrases


def get_earliest_comment_date(comments: list[Comment]) -> datetime.date:
    earliest_date = datetime.date(9999, 1, 1)
    for comment in comments:
        if comment.date < earliest_date:
            earliest_date = comment.date
    return earliest_date


def get_latest_comment_date(comments: list[Comment]) -> datetime.date:
    latest_date = datetime.date(1, 1, 1)
    for comment in comments:
        if comment.date > latest_date:
            latest_date = comment.date
    return latest_date
