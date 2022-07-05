from database_interaction.db_connection import connection


class FavoriteChannel:
    def __init__(self, channel_id: str):
        self.channel_id = channel_id


def get_favorite_user_channels(user_telegram_id: int, limited: bool = False) -> [FavoriteChannel]:
    """Получить список избранных каналов у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT channel_url
FROM public.favorite_channel
WHERE user_id = %s
                """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: FavoriteChannel(x[0]), curs)


def delete_favorite_user_channel(user_telegram_id: int, favorite_channel: FavoriteChannel):
    """Удалить видео из списка избранного у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
DELETE FROM public.favorite_channel
WHERE user_id = %s AND channel_url = %s
            """, (user_telegram_id, favorite_channel.channel_id))


class FavoriteVideo:
    def __init__(self, url: str):
        self.url = url


def get_favorite_user_videos(user_telegram_id: int, limited: bool = False) -> [FavoriteVideo]:
    """Получить список избранных видео у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT url
FROM public.favorite_video
WHERE user_id = %s
                """ + ' LIMIT 10' if limited else '', (user_telegram_id,))
            return map(lambda x: FavoriteVideo(x[0]), curs)


def delete_favorite_user_video(user_telegram_id: int, favorite_video: FavoriteVideo):
    """Удалить видео из списка избранного у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
DELETE FROM public.favorite_video
WHERE user_id = %s AND url = %s
            """, (user_telegram_id, favorite_video.url))


