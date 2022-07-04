from database_interaction.db_connection import connection


def insert_video(channel_id: str, video_id: str):
    """Добавить видео в базу"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute('INSERT INTO public.video('
                         'url, channel_url, last_scrap_date) '
                         f'VALUES (%s, %s, current_timestamp);', (video_id, channel_id))


def update_scrap_date(video_id: str):
    """Обновить дату последней подгрузки комментариев"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute('UPDATE public.video '
                         'SET last_scrap_date = current_timestamp '
                         f'WHERE url = %s;', (video_id,))
