from datetime import datetime

from database_interaction import auth
from database_interaction.db_connection import connection


class HistoryChannel:
    def __init__(self, channel_id: str, viewing_date: datetime):
        self.channel_id = channel_id
        self.viewing_date = viewing_date


def get_all_channel_history() -> [HistoryChannel]:
    """Получить весь список истории по анализу каналов у всех пользователей"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
channel_url, viewing_date
FROM
public.history_channel;
ORDER BY viewing_date DESC
            """)
            return list(map(lambda x: HistoryChannel(x[0], x[1]), curs))


def get_user_channel_history(user_id: int, limited: bool = False) -> [HistoryChannel]:
    """Получить список истории по анализу канала у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
channel_url, viewing_date
FROM public.history_channel
WHERE user_id = %s
ORDER BY viewing_date DESC
            """ + (' LIMIT 10' if limited else ' '), (user_id,))
            return list(map(lambda x: HistoryChannel(x[0], x[1]), curs))


class HistoryVideo:
    def __init__(self, url: str, viewing_date: datetime):
        self.url = url
        self.viewing_date = viewing_date


def get_all_video_history() -> [HistoryVideo]:
    """Получить весь список истории по анализу видео у всех пользователей"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
url, viewing_date
FROM public.history_video
            """)
            return list(map(lambda x: HistoryVideo(x[0], x[1]), curs))


def get_user_video_history(user_id: int, limited: bool = False) -> [HistoryVideo]:
    """Получить список истории по анализу видео у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
url, viewing_date
FROM public.history_video
WHERE user_id = %s
            """ + (' LIMIT 10' if limited else ' '), (user_id,))
            return list(map(lambda x: HistoryVideo(x[0], x[1]), curs))
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
channel_url, viewing_date
FROM public.history_channel
WHERE user_id = %s
ORDER BY viewing_date DESC
            """ + (' LIMIT 10' if limited else ' '), (user_id,))
            return list(map(lambda x: HistoryChannel(x[0], x[1]), curs))


def add_user_history_video(user_id: int, video_id: str):
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.history_video(
    user_id, url, viewing_date)
    VALUES (%s, %s, current_timestamp);
            """, (user_id, video_id))


def add_user_channel_video(user_id: int, channel_id: str):
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.history_channel(
    user_id, channel_url, viewing_date)
    VALUES (%s, %s, current_timestamp);
            """, (user_id, channel_id))


def get_video_requests_count_for_last_parameter(parameter: str) -> int:
    """Получить количество запросов видео за последний промежуток у всех
    :param parameter '1 month', '3 days' и т.д."""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT COUNT (
SELECT * FROM public.history_video
WHERE viewing_date >= now() - interval '{parameter}'
)
            """)
            return curs.fetchone()[0]


def get_new_users_count_for_last_parameter(parameter: str) -> int:
    """Получить количество запросов видео за сколько-то у всех
    :param parameter '1 month', '3 days' и т.д."""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT COUNT (
SELECT * FROM public.users;
WHERE enter_date >= now() - interval '{parameter}'
)
            """)
            return curs.fetchone()[0]


def get_channel_requests_count_for_last_parameter(parameter: str) -> int:
    """Получить количество запросов видео за сколько-то у всех
    :param parameter '1 month', '3 days' и т.д."""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT COUNT (
SELECT * FROM public.users;
WHERE viewing_date >= now() - interval '{parameter}'
)
            """)
            return curs.fetchone()[0]


# if auth.get_login_exists(login):


def get_user_video_requests_count_for_last_parameter(parameter: str, login: str) -> int:
    """Получить количество запросов видео за последний промежуток у пользователя
    :param parameter '1 month', '3 days' и т.д."""
    if auth.get_login_exists(login):
        user_id = auth.get_user_id(login)
        with connection as connect:
            with connect.cursor() as curs:
                curs.execute(f"""
SELECT COUNT (
SELECT * FROM public.history_video
WHERE viewing_date >= now() - interval '{parameter}' AND user_id = %s
)
                """, (user_id,))
                return curs.fetchone()[0]


def get_user_channel_requests_count_for_last_parameter(parameter: str, login: str) -> int:
    """Получить количество запросов видео за последний промежуток у пользователя
    :param parameter '1 month', '3 days' и т.д."""
    if auth.get_login_exists(login):
        user_id = auth.get_user_id(login)
        with connection as connect:
            with connect.cursor() as curs:
                curs.execute(f"""
SELECT COUNT (
SELECT * FROM public.users;
WHERE viewing_date >= now() - interval '{parameter}'
)
            """, (user_id,))
                return curs.fetchone()[0]

