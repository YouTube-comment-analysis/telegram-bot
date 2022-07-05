from datetime import datetime
from database_interaction.db_connection import connection
from database_interaction.favorite import FavoriteChannel, FavoriteVideo


class HistoryChannel(FavoriteChannel):
    def __init__(self, channel_id: str, viewing_date: datetime):
        FavoriteChannel.__init__(self, channel_id)
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
            return map(lambda x: HistoryChannel(x[0], x[1]), curs)


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
            """ + ' LIMIT 10' if limited else '', (user_id,))
            return map(lambda x: HistoryChannel(x[0], x[1]), curs)


class HistoryVideo(FavoriteVideo):
    def __init__(self, url: str, viewing_date: datetime):
        FavoriteVideo.__init__(self, url)
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
            return map(lambda x: HistoryVideo(x[0], x[1]), curs)


def get_user_video_history(user_id: int, limited: bool = False) -> [HistoryVideo]:
    """Получить список истории по анализу видео у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT
url, viewing_date
FROM public.history_video
WHERE user_id = %s
            """ + ' LIMIT 10' if limited else '', (user_id,))
            return map(lambda x: HistoryVideo(x[0], x[1]), curs)
