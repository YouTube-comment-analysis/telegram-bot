import logging
import re
import time

from aiogram.utils import json
import requests

logging.basicConfig(level=logging.INFO)

SESSION_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'


class PostInformation:
    key = None
    ytcfg = None
    context = None
    token = None


def get_get_response(url: str):
    for i in range(5):
        response = requests.get(url)
        if response.status_code == 200:
            break
        logging.warning(f'Неверный статус ответа с {url} (попытка №{i})')
        time.sleep(3)

    return response


def get_post_response(url: str, post_information: PostInformation, session):
    data = {'context': post_information.context, 'continuation': post_information.token}
    for i in range(5):
        response = session.post(url, params={'key': post_information.key}, json=data)
        if response.status_code == 200:
            break
        logging.warning(f'Неверный статус ответа с {url} (попытка №{i})')
        time.sleep(3)

    return response


def get_post_information(get_response_text: str) -> PostInformation:
    post_information = PostInformation()
    post_information.key = get_response_text.split('INNERTUBE_API_KEY":"')[1].split('"')[0]
    post_information.ytcfg = json.loads(re.search(r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;', get_response_text).group(1))
    post_information.context = post_information.ytcfg['INNERTUBE_CONTEXT']
    return post_information


def remove_duplicates(elements: list):
    i = 0
    while i < len(elements) - 1:
        j = i + 1
        while j < len(elements):
            if elements[i] == elements[j]:
                elements.pop(j)
                j -= 1
            j += 1
        i += 1