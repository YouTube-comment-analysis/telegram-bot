from database_interaction.db_connection import connection


def add_favorite_user_channel(user_id: int, channel_id: str):
    """Добавить канал в избранное"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.favorite_channel(
user_id, channel_url)
VALUES (%s, %s);
            """, (user_id, channel_id))


def add_favorite_user_video(user_id: int, video_id: str):
    """Добавить Видео в избранное"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.favorite_video(
user_id, url)
VALUES (%s, %s);
            """, (user_id, video_id))


def get_favorite_user_channels(user_id: int, limited: bool = False) -> [str]:
    """Получить список избранных каналов у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
select channel_url from (
SELECT *, row_number() over( order by (select 1)) rowid 
  FROM public.favorite_channel 
  ) x 
  WHERE user_id = %s
  order by rowid desc
            """ + (' LIMIT 10' if limited else ' '), (user_id,))
            return list(map(lambda x: x[0], curs))


def delete_favorite_user_channel(user_id: int, favorite_channel: str):
    """Удалить видео из списка избранного у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
DELETE FROM public.favorite_channel
WHERE user_id = %s AND channel_url = %s
            """, (user_id, favorite_channel))


def get_favorite_user_videos(user_id: int, limited: bool = False) -> [str]:
    """Получить список избранных видео у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
select url from (
SELECT *, row_number() over( order by (select 1)) rowid 
  FROM public.favorite_video 
  ) x 
  WHERE user_id = %s
  order by rowid desc
                """ + (' LIMIT 10' if limited else ' '), (user_id,))
            return list(map(lambda x: x[0], curs))


def delete_favorite_user_video(user_id: int, favorite_video: str):
    """Удалить видео из списка избранного у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
DELETE FROM public.favorite_video
WHERE user_id = %s AND url = %s
            """, (user_id, favorite_video))


