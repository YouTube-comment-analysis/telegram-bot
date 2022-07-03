import psycopg2 as db
from config import database_config

connection = db.connect(
    database=database_config['database'],
    user=database_config['user'],
    password=database_config['password'],
    host=database_config['host'],
    port=database_config['port']
)


def extract_comments(video_id: str, ordered: bool):
    cursor = connection.cursor()
    result = []
    if ordered:
        cursor.execute('SELECT text, writing_date, likes, popular_order, is_reply '
                       'FROM public.commentary WHERE '
                       f'url = %s', (video_id,))
        result = cursor.fetchall()
    else:
        cursor.execute('SELECT text, writing_date, likes, popular_order, is_reply '
                       'FROM public.commentary WHERE '
                       f'url = %s', (video_id,))
        result = cursor.fetchall()
    cursor.close()
    return result


def load_comments(video_id: str, comments: []):
    with connection as connect:
        with connect.cursor() as curs:
            for row in comments:
                curs.execute('INSERT INTO public.commentary('
                             'url, text, writing_date, likes, popular_order, is_reply) '
                             f'VALUES (%s, %s, %s, %s, %s, %s)',
                             (video_id, row.text, row.writting_date, row.likes, row.popular_order, row.is_reply))


def insert_video(channel_id: str, video_id: str):
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute('INSERT INTO public.video('
                         'url, channel_url, last_scrap_date) '
                         f'VALUES (%s, %s, current_timestamp);', (video_id, channel_id))


def update_scrap_date(video_id: str):
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute('UPDATE public.video '
                         'SET last_scrap_date = current_timestamp '
                         f'WHERE url = %s;', (video_id,))


def insert_channel(channel_id: str):
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute('INSERT INTO public.channel('
                         'channel_url) '
                         f'VALUES (%s);', (channel_id,))
