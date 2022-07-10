from database_interaction.db_connection import connection


def insert_channel(channel_id: str):
    if not exists_channel(channel_id):
        """Добавить канал в базу"""
        with connection as connect:
            with connect.cursor() as curs:
                curs.execute("""
    INSERT INTO public.channel
        (channel_url)
        VALUES (%s)
                """, (channel_id,))


def exists_channel(channel_id: str) -> bool:
    """Проверить существует ли канал в базе"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT EXISTS(
    SELECT * FROM public.channel
    WHERE channel_url = %s
)
            """, (channel_id,))
            return curs.fetchone()[0]


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
