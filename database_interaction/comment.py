from database_interaction.db_connection import connection


def extract_comments(video_id: str, ordered_by_date: bool):
    """Скачать все комментарии к видео. Можно выбрать сортировку по дате, иначе по популярности"""
    with connection as connect:
        with connect.cursor() as curs:
            if ordered_by_date:
                curs.execute("""
SELECT url, text, writing_date, likes, popular_order, is_reply
    FROM public.commentary
    WHERE url = %s
    ORDER BY writing_date
                """, (video_id,))
                return curs.fetchall()
            else:
                curs.execute("""
SELECT url, text, writing_date, likes, popular_order, is_reply
    FROM public.commentary
    WHERE url = %s
    ORDER BY popular_order
                """, (video_id,))
                return curs.fetchall()


def load_comments(video_id: str, comments: []):
    """Загрузить дополнительные комментарии к видео"""
    with connection as connect:
        with connect.cursor() as curs:
            for row in comments:
                curs.execute("""
INSERT INTO public.commentary(
    url, text, writing_date, likes, popular_order, is_reply)
    VALUES (%s, %s, %s, %s, %s, %s)
                """, (video_id, row.text, row.writting_date, row.likes, row.popular_order, row.is_reply))







