from datetime import datetime
from database_interaction.db_connection import connection


class ChannelHistory:
    def __init__(self, user_id: int, channel_id: str, viewing_date: datetime):
        self.user_id = user_id
        self.channel_id = channel_id,
        self.viewing_date = viewing_date


def get_all_channel_history() -> [ChannelHistory]:
    """Получить весь список истории по анализу каналов у всех пользователей"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
user_id, channel_url, viewing_date
FROM
public.history_channel;
ORDER BY viewing_date DESC
                """)
            return map(lambda x: ChannelHistory(x[0], x[1], x[2]), curs)


def get_user_channel_history(user_telegram_id: int, limited: bool = False) -> [ChannelHistory]:
    """Получить список истории по анализу канала у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
user_id, channel_url, viewing_date
FROM public.history_channel
WHERE user_id = %s
ORDER BY viewing_date DESC
                """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: ChannelHistory(x[0], x[1], x[2]), curs)


class VideoHistory:
    def __init__(self, user_id: int, url: str, viewing_date: datetime):
        self.user_id = user_id
        self.url = url,
        self.viewing_date = viewing_date


def get_all_video_history() -> [ChannelHistory]:
    """Получить весь список истории по анализу видео у всех пользователей"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
user_id, url, viewing_date
FROM public.history_video
                """)
            return map(lambda x: VideoHistory(x[0], x[1], x[2]), curs)


def get_user_video_history(user_telegram_id: int, limited: bool = False) -> [ChannelHistory]:
    """Получить список истории по анализу видео у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
user_id, url, viewing_date
FROM public.history_video
WHERE user_id = %s
                """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: ChannelHistory(x[0], x[1], x[2]), curs)
