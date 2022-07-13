import datetime

import requests
from youtubesearchpython import ChannelsSearch

from scraping import searching


def is_video_url_correct(url: str) -> bool:
    if 'https://www.youtube.com/watch?v=' not in url:
        return False
    response = searching.get_get_response(url)
    if response.status_code != 200:
        return False
    return 'videoPrimaryInfoRenderer' in response.text


def is_channel_url_correct(url: str) -> bool:
    if ('https://www.youtube.com/' not in url) or ('/channels' in url) or ('/videos' in url) or ('/featured' in url):
        return False
    response = searching.get_get_response(url)
    if response.status_code != 200:
        return False
    return 'gridVideoRenderer' in response.text


def get_video_post_date(url) -> datetime.date:
    response = requests.get(url)
    date = datetime.datetime.strptime(response.text.split('uploadDate":"')[1].split('"')[0], '%Y-%m-%d')
    return date.date()


def get_chanel_url_by_video(video_url: str) -> str:
    resource = requests.get(video_url)
    return 'https://www.youtube.com' + resource.text.split('"canonicalBaseUrl":"')[1].split('"')[0]


def get_video_comments_amount(url: str) -> int:
    response = searching.get_get_response(url)

    session = requests.Session()
    session.headers['user-Agent'] = searching.SESSION_USER_AGENT

    post_information = searching.get_post_information(response.text)
    post_information.token = response.text.split('continuationCommand":{"token":"')[1].split('"')[0]

    response = searching.get_post_response('https://www.youtube.com/youtubei/v1/next', post_information, session)
    js = response.json()
    session.close()

    if 'reloadContinuationItemsCommand' in js['onResponseReceivedEndpoints'][0]:
        return int(js['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0][
                       'commentsHeaderRenderer']['countText']['runs'][0]['text'].replace(r' ', ''))
    else:
        return 0


def get_channel_url_by_name(name: str):
    """
    Получает url канала по его названию

    :param name: Название канала
    :return: url канала
    """
    response = ChannelsSearch(name, limit=1, region='RU')
    if str(response.responseSource)[3:18] == "channelRenderer":
        link = response.resultComponents[0]['link']
        return link
