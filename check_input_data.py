import re
from datetime import datetime

from dateparser import date


class CheckInputData:
    @staticmethod
    def phone_number(phone: str) -> bool:
        """Проверка номера телефона"""
        a = phone.startswith('79')
        b = True
        for char in phone:
            if not char.isdigit():
                b = False
        c = len(phone) == 11
        return a * b * c

    @staticmethod
    def email(mail: str) -> bool:
        """Проверка почты"""
        a = '@' in mail
        b = '.' in mail.split('@')[1]
        return a * b

    @staticmethod
    def russian_chars(string: str):
        """Проверка на содержание только русских букв"""
        small_alp = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        big_alp = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ'
        a = string[0] in big_alp
        b = True
        for char in string[1:]:
            if char not in small_alp:
                b = False
                break
        d = len(string) > 1
        return a * b * d

    @staticmethod
    def check_youtube_video_url(url: str):
        """Проверить ссылку на ютуб видео"""
        return 'https://www.youtube.com/watch?v=' in url

    @staticmethod
    def check_youtube_channel_url(url: str):
        """Проверить ссылку на ютуб канал"""
        return 'https://www.youtube.com/c/' in url


    @staticmethod
    def date_lesser_check(first: datetime, second: date) -> bool:
        return first < second

