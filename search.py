import re
import time

from aiogram.utils import json
from youtubesearchpython import ChannelsSearch
import requests

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


print(get_video_comments_count('https://www.youtube.com/watch?v=2mchGs-1E6E'))