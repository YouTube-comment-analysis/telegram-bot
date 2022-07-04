from datetime import datetime
from database_interaction.db_connection import connection


class ChannelFavorite:
    def __init__(self, channel_id: str):
        self.channel_id = channel_id


def get_favorite_user_channels(user_telegram_id: int, limited: bool = False) -> [ChannelFavorite]:
    """Получить список избранных каналов у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT channel_url
FROM public.favorite_channel
WHERE user_id = %s
                """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: ChannelFavorite(x[0]), curs)


class VideoHistory:
    def __init__(self, url: str):
        self.url = url


def delete_favorite_user_channel(user_telegram_id: int, limited: bool = False) -> [VideoHistory]:
    """Получить список избранных каналов у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT url
FROM public.favorite_video;
WHERE user_id = %s
            """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: VideoHistory(x[0]), curs)





