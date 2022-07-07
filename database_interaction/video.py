import enum
from datetime import datetime
from database_interaction.db_connection import connection


def insert_video(channel_id: str, video_id: str):
    """Добавить видео в базу"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO 
public.video(url, channel_url, last_scrap_date)
VALUES (%s, %s, current_timestamp)
            """, (video_id, channel_id))


class ScrapBy(enum.Enum):
    date = ['last_by_date_scrap', 'comments_by_date']
    popular = ['last_popular_scrap', 'comments_by_popular']


def update_scrap_date(video_id: str, scrap_by: ScrapBy, new_value: datetime):
    """Обновить дату последней подгрузки комментариев"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
UPDATE public.video
    SET {scrap_by.value[0]} = %s
    WHERE url = %s
            """, (new_value, video_id))


def update_scrap_count(video_id: str, scrap_by: ScrapBy, new_value: int):
    """Обновить количество последней подгрузки комментариев"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
UPDATE public.video
    SET {scrap_by.value[1]} = %s
    WHERE url = %s
            """, (new_value, video_id))


def get_scrap_date(video_id: str, scrap_by: ScrapBy) -> int:
    """Получить дату последней подгрузки комментариев"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT {scrap_by.value[0]}
FROM public.video
WHERE url = %s
            """, (video_id,))
            data = curs.fetchone()
            return data[0] if data is not None else 0


def get_scrap_count(video_id: str, scrap_by: ScrapBy) -> int:
    """Получить количество последней подгрузки комментариев"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT {scrap_by.value[1]}
FROM public.video
WHERE url = %s
            """, (video_id,))
            data = curs.fetchone()
            return data[0] if data is not None else 0


def get_all_scrap_info(video_id: str) -> dict:
    """
    Получить всю информацию о последних загрузках
    :return Возвращает словарь с ключами 'last_popular', 'popular_comments', 'last_date', 'date_comments'
    """
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT last_popular_scrap, comments_by_popular, last_by_date_scrap, comments_by_date 
FROM public.video
WHERE url = %s
                """, (video_id,))
            data = curs.fetchone()
            return {'last_popular': data[0], 'popular_comments': data[1],
                    'last_date': data[2], 'date_comments': data[3]}


def video_exists(video_id: str) -> bool:
    """Получить содержится ли видео в базе"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT EXISTS(
    SELECT * FROM public.video
    WHERE url = %s
)
            """, (video_id,))
            return curs.fetchone()[0]
