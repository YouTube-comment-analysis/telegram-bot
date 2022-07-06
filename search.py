import re
import time

import dateparser
from aiogram.utils import json
from youtubesearchpython import ChannelsSearch
import requests

from comment import Comment

SESSION_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'


def regex_search(text, pattern, group=1, default=None):
    match = re.search(pattern, text)
    return match.group(group) if match else default


def get_videos_by_channel_url(url):
    session = requests.Session()
    session.headers['User-Agent'] = SESSION_USER_AGENT

    for _ in range(5):
        response = requests.get(url + "/videos")
        if response.status_code == 200:

            result = re.findall(r'(/watch\?v=.*?)"', str(response.text))
            text = response.text
            key = text.split('INNERTUBE_API_KEY":"')[1].split('"')[0]
            ytcfg = json.loads(re.search(r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;', text).group(1))
            context = ytcfg['INNERTUBE_CONTEXT']

            while text.find('"token":"') != -1:
                token = text.split('"token":"')[1].split('"')[0]
                data = {'context': context,
                        'continuation': token}

                response = session.post('https://www.youtube.com/youtubei/v1/browse', params={'key': key}, json=data)

                result += re.findall(r'(/watch\?v=.*?)"', str(response.text))
                text = response.text.replace('\n', '').replace(' ', '')

            return result

        else:
            time.sleep(20)


def get_channel_url_by_name(name):
    response = ChannelsSearch(name, limit=1, region='RU')
    if str(response.responseSource)[3:18] == "channelRenderer":
        link = response.resultComponents[0]['link']
        return link


def get_video_comments_count(url):
    response = requests.get(url)

    session = requests.Session()
    session.headers['User-Agent'] = SESSION_USER_AGENT
    key = response.text.split('INNERTUBE_API_KEY":"')[1].split('"')[0]
    ytcfg = json.loads(re.search(r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;', response.text).group(1))
    context = ytcfg['INNERTUBE_CONTEXT']
    token = response.text.split('continuationCommand":{"token":"')[1].split('"')[0]
    data = {'context': context,
            'continuation': token}

    response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)

    return response.text.split('"text": "')[1].split('"')[0].replace(' ','')


def remove_dublicats(list):
    i = 0
    while i < len(list)-1:
        j = i+1
        while j < len(list):
            if list[i] == list[j]:
                list.pop(j)
                j -= 1
            j += 1
        i += 1


def get_comment_from_comment_data(json):
    comment = Comment()

    comment.text = ''
    for text_data in json['contentText']['runs']:
        comment.text += text_data['text']

    time_text = json['publishedTimeText']['runs'][0][
        'text']
    comment.date = str(dateparser.parse(time_text.split('(')[0].strip()).date())

    if 'voteCount' in json:
        comment.votes = json['voteCount']['simpleText']
    else:
        comment.votes = 0

    return comment


def get_comments_from_video(url, is_sort_by_recent_needed=False):
    response = requests.get(url)

    session = requests.Session()
    session.headers['User-Agent'] = SESSION_USER_AGENT
    key = response.text.split('INNERTUBE_API_KEY":"')[1].split('"')[0]
    ytcfg = json.loads(re.search(r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;', response.text).group(1))
    context = ytcfg['INNERTUBE_CONTEXT']
    token = response.text.split('continuationCommand":{"token":"')[1].split('"')[0]
    data = {'context': context, 'continuation': token}

    response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)
    js = response.json()

    if is_sort_by_recent_needed:
        token = js['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]\
            ['commentsHeaderRenderer']['sortMenu']['sortFilterSubMenuRenderer']['subMenuItems'][1]['serviceEndpoint']\
            ['continuationCommand']['token']
        data = {'context': context, 'continuation': token}
        response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)
        js = response.json()

    comments = []

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
                comments.append(comment)

                if 'replies' in comment_data['commentThreadRenderer']:
                    tokens.append(comment_data['commentThreadRenderer']['replies']['commentRepliesRenderer']['contents'][0]
                                  ['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token'])

        for token in tokens:
            data = {'context': context, 'continuation': token}
            response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)
            new_js = response.json()

            if 'continuationItems' in new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']:
                print('Считывается группа из ' + str(len(new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems'])) + ' комментариев')
                is_sub_end = False
                while not is_sub_end:
                    is_sub_end = True
                    for comment_data in new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems']:
                        if 'commentRenderer' in comment_data:
                            comment = get_comment_from_comment_data(comment_data['commentRenderer'])
                            comment.is_reply = True
                            comments.append(comment)

                    last_comment_data = new_js['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems'][-1]
                    if 'commentRenderer' not in last_comment_data:
                        sub_token = last_comment_data['continuationItemRenderer']['button']['buttonRenderer']['command']['continuationCommand']['token']
                        data = {'context': context, 'continuation': sub_token}
                        response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)
                        new_js = response.json()
                        is_sub_end = False
                        print('Открываются остальные комментарии')

        last_comment_data = js['onResponseReceivedEndpoints'][index][continuation_name]['continuationItems'][-1]
        if 'continuationItemRenderer' in last_comment_data:
            token = last_comment_data['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
            data = {'context': context, 'continuation': token}
            response = session.post('https://www.youtube.com/youtubei/v1/next', params={'key': key}, json=data)
            js = response.json()
            is_end = False
            print('Загружена следующая страница')

        index = 0
        continuation_name = 'appendContinuationItemsAction'

    return comments




