import datetime
import logging
import re

import dateparser
import requests

from comment import Comment
from scraping import searching, getting_information

from scraping.getting_information import get_video_post_date
from scraping.searching import get_get_response


def get_list_of_channel_videos_with_comment_count(channel_url: str, start_date: datetime.date, end_date: datetime.date) -> list[dict[str, int]]:
    """
    Получает список видеороликов с количеством комментариве с заданного канала по заданному интервалу

    :param channel_url:
    :param start_date:
    :param end_date:
    :return: {'url': <url ролика>, 'comment_count': <количество комментариев ролика>}
    """

    video_urls = get_video_ids_by_channel_url(channel_url)
    for i in range(len(video_urls)):
        video_urls[i] = 'https://www.youtube.com' + video_urls[i]

    video_urls = get_videos_in_date_interval(video_urls, start_date, end_date)

    logging.info('Запуск подсчета количества комментариве под видео')
    dic_list = []
    for url in video_urls:
        dic_list.append({'url': url, 'comment_count': getting_information.get_video_comments_amount(url)})
        logging.info(f'{len(dic_list)}/{len(video_urls)}')

    return dic_list


def get_video_index_by_date(urls: list[str], date: datetime.date, side=-1) -> int:
    """
    Находит индекс ролика в списке, соответствющего заданной дате публикации

    :param urls: список url роликов
    :param date: искомая дата публикации ролика
    :param side: -1 взять ролик с ближайшей меньшей датой; 1 взять ролик с ближайшей большей датой
    :return: индекс в массиве, соответствующий видеоролику с искомой датой публикации
    """
    first = 0
    mid = 0
    last = len(urls) - 1
    while first <= last:
        mid = (first + last) // 2
        cur_val = get_video_post_date(urls[mid])
        if (cur_val < date) or ((cur_val == date) and (side == -1)):
            last = mid - 1
        else:
            first = mid + 1
    return first if side == -1 else last if side == 1 else mid


def get_video_ids_by_channel_url(url: str) -> [str]:
    """
    Возвращает список всех видео канала

    :param url: url канала
    :return: Список id видеороликов
    """
    logging.info('Запуск поиска всех видео канала')
    session = requests.Session()
    session.headers['User-Agent'] = searching.SESSION_USER_AGENT

    response = get_get_response(url + "/videos")
    if response.status_code == 200:
        text = response.text
        video_urls = re.findall(r'(/watch\?v=.*?)"', str(text))
        post_information = searching.get_post_information(text)

        while text.find('"token":"') != -1:
            post_information.token = text.split('"token":"')[1].split('"')[0]
            response = searching.get_post_response('https://www.youtube.com/youtubei/v1/browse', post_information, session)

            if response.status_code == 200:
                video_urls += re.findall(r'(/watch\?v=.*?)"', str(response.text))
                text = response.text.replace('\n', '').replace(' ', '')

        session.close()
        return video_urls
    else:
        session.close()
        return []


def get_videos_in_date_interval(urls: list[str], start_date: datetime.date, end_date: datetime.date) -> list[str]:
    logging.info('Запуск отбора роликов из нужного временного интервала')
    last_date = get_video_post_date(urls[0])
    first_date = get_video_post_date(urls[-1])
    if (end_date < first_date) | (start_date > last_date):
        return []

    last_index = get_video_index_by_date(urls, start_date, 1)
    result = urls[0:last_index + 1]
    first_index = get_video_index_by_date(urls, end_date, -1)
    result = result[first_index:]
    return result


# ----------------------


def get_comments_from_video_iterator(url: str, is_sort_by_recent_needed=False, are_replies_needed=True):
    response = get_get_response(url)

    session = requests.Session()
    session.headers['User-Agent'] = searching.SESSION_USER_AGENT

    post_information = searching.get_post_information(response.text)
    post_information.token = response.text.split('continuationCommand":{"token":"')[1].split('"')[0]

    response = searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
    js = response.json()

    if is_sort_by_recent_needed:
        post_information.token = js['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand'] \
            ['continuationItems'][0]['commentsHeaderRenderer']['sortMenu']['sortFilterSubMenuRenderer'] \
            ['subMenuItems'][1]['serviceEndpoint']['continuationCommand']['token']

        searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
        js = response.json()

    is_end = False
    index = 1
    continuation_name = 'reloadContinuationItemsCommand'
    while not is_end:
        is_end = True

        tokens = []
        for comment_data in js['onResponseReceivedEndpoints'][index][continuation_name]['continuationItems']:
            if 'continuationItemRenderer' not in comment_data:
                comment = get_comment_from_comment_data(comment_data['commentThreadRenderer']['comment']['commentRenderer'])
                comment.is_reply = False
                comment.video_url = url.split('watch?v=')[1]
                yield comment

                if are_replies_needed:
                    if 'replies' in comment_data['commentThreadRenderer']:
                        tokens.append(
                            comment_data['commentThreadRenderer']['replies']['commentRepliesRenderer']['contents'][0]
                            ['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token'])

        for token in tokens:
            post_information.token = token
            response = searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
            new_js = response.json()

            if 'continuationItems' in new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']:
                is_sub_end = False
                while not is_sub_end:
                    is_sub_end = True
                    for comment_data in new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems']:
                        if 'commentRenderer' in comment_data:
                            comment = get_comment_from_comment_data(comment_data['commentRenderer'])
                            comment.is_reply = True
                            comment.video_url = url.split('watch?v=')[1]
                            yield comment

                    last_comment_data = new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems'][-1]
                    if 'commentRenderer' not in last_comment_data:
                        post_information.token = last_comment_data['continuationItemRenderer']['button']['buttonRenderer']['command']['continuationCommand']['token']
                        response = searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
                        new_js = response.json()
                        is_sub_end = False

        last_comment_data = js['onResponseReceivedEndpoints'][index][continuation_name]['continuationItems'][-1]
        if 'continuationItemRenderer' in last_comment_data:
            post_information.token = last_comment_data['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
            response = searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
            js = response.json()
            is_end = False

        index = 0
        continuation_name = 'appendContinuationItemsAction'


def get_comment_from_comment_data(json) -> Comment:
    comment = Comment()

    comment.id = json['commentId']

    comment.text = ''
    for text_data in json['contentText']['runs']:
        comment.text += text_data['text']

    time_text = json['publishedTimeText']['runs'][0][
        'text']
    comment.date = dateparser.parse(time_text.split('(')[0].strip()).date()

    if 'voteCount' in json:
        comment.votes = json['voteCount']['simpleText']
    else:
        comment.votes = 0

    return comment
