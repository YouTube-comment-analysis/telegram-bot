from database_interaction.db_connection import connection


def insert_channel(channel_id: str):
    """Добавить канал в базу"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.channel
    (channel_url)
    VALUES (%s)
            """, (channel_id,))


def get_channel_videos(channel_id: str) -> [str]:
    """Получить все url_id на загруженные видео с канала"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT url
    FROM public.video
    WHERE channel_url = %s
            """, (channel_id,))
            return map(lambda x: x[0], curs)
