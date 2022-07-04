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
