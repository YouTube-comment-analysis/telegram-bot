import datetime
import math

import numpy as np
import pymorphy2
from matplotlib import pyplot as plt
from analysis import auxiliary
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from comment import Comment


model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())
morph = pymorphy2.MorphAnalyzer()
auxiliary.set_plt_params(plt)


def make_sentiment_analysis_hist(comments: list[Comment], grouping: auxiliary.GroupingType, start_date=None, end_date=None, image_name='hist') -> str:
    """
    Строит гистограмму тональности комментариев по датам
    :param comments: список комментариев
    :param grouping: 'day' или 'week' или 'month' (определяет на какие промежутки будет разбит интервал )
    :param start_date: начало интервала для анализа (None для автовыбора)
    :param end_date: конец интервала для анализа (None для автовыбора)
    :param image_name: имя файла (использовать телеграм id)
    :return: относительный путь к диаграмме
    """
    if start_date is None:
        start_date = auxiliary.get_earliest_comment_date(comments)
    if end_date is None:
        end_date = auxiliary.get_latest_comment_date(comments)

    date_comments = auxiliary.get_comments_in_date(comments, start_date, end_date)

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

    pair = get_dates_with_counts(dates, moods, grouping, start_date, end_date)

    return save_sentiment_hist(pair['dates'], pair['counts'], grouping, image_name)


def get_sentiment_predicts(comments: list[Comment]) -> list[dict[str, float]]:
    texts = []
    for comment in comments:
        texts.append(comment.text)
    return model.predict(texts, k=1)


def get_dates_with_counts(dates: list[datetime.date], moods: list, grouping: auxiliary.GroupingType, start_date: datetime.date, end_date: datetime.date) -> dict:
    interval = auxiliary.get_interval_len(grouping, start_date, end_date)

    counts = []
    for j in range(3):
        counts.append([0 for i in range(interval)])

    for i in range(len(moods)):
        if grouping == auxiliary.GroupingType.day:
            counts[moods[i]][(dates[i] - start_date).days] += 1
        elif grouping == auxiliary.GroupingType.week:
            counts[moods[i]][math.ceil(((dates[i] - start_date).days+1) / 7) - 1] += 1
        elif grouping == auxiliary.GroupingType.month:
            counts[moods[i]][(dates[i].year - start_date.year) * 12 + (dates[i].month - start_date.month)] += 1

    result_dates = [0 for j in range(interval)]
    for i in range(len(result_dates)):
        if grouping == auxiliary.GroupingType.day:
            result_dates[i] = (start_date + datetime.timedelta(days=i))
        elif grouping == auxiliary.GroupingType.week:
            result_dates[i] = (start_date + datetime.timedelta(days=i * 7))
        elif grouping == auxiliary.GroupingType.month:
            result_dates[i] = datetime.date(start_date.year + (start_date.month + i - 1) // 12,
                                     (start_date.month + i - 1) % 12 + 1, 15)

    return {'dates': result_dates, 'counts': counts}


def save_sentiment_hist(dates: list[datetime.date], counts: list[int], grouping: auxiliary.GroupingType, image_name: str) -> str:
    plt.style.use('bmh')

    fig, ax = plt.subplots()

    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    width = 0.25
    r = np.arange(len(dates))

    plt.bar(r, counts[0], width=width, label='позитивные', color='lime')
    plt.bar(r + width, counts[1], width=width, label='негативные', color='red')
    plt.bar(r + 2*width, counts[2], width=width, label='нейтральные', color='tan')

    str_dates = []
    if (grouping == auxiliary.GroupingType.day) or (grouping == auxiliary.GroupingType.week):
        for i in range(len(dates)):
            if i % math.ceil(len(dates)/25) == 0:
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
    path = r'photos/' + str(image_name) + '.png'
    plt.savefig(path, dpi=200)
    plt.clf()

    return path
