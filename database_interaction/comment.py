from database_interaction.db_connection import connection
from comment_scrapping.comment import Comment


def extract_comments(video_id: str, ordered_by_date: bool = False) -> [Comment]:
    """Скачать все комментарии к видео. Можно выбрать сортировку по дате, иначе по популярности"""
    with connection as connect:
        with connect.cursor() as curs:
            if ordered_by_date:
                curs.execute("""
SELECT url, text, writing_date, likes, is_reply
    FROM public.commentary
    WHERE url = %s
    ORDER BY writing_date DESC
                """, (video_id,))
            else:
                curs.execute("""
SELECT url, text, writing_date, likes, is_reply
    FROM public.commentary
    WHERE url = %s
    ORDER BY popular_order
                """, (video_id,))

            return map(lambda x: Comment(
                video_url=x['0'],
                text=x['1'],
                date=x['2'],
                votes=x['3'],
                is_reply=x['4']
            ), curs)


def load_comments(video_id: str, comments: [Comment], in_popular_order: bool):
    """**Загрузить дополнительные комментарии к видео**
       :param in_popular_order Комментарии отсортированы по популярности? Иначе индексу популярности будет присвоено max int
       :param video_id Видео
       :param comments: Массив комментариев
    """
    with connection as connect:
        with connect.cursor() as curs:
            count = 1
            for row in comments:
                curs.execute("""
INSERT INTO public.commentary(
    url, text, writing_date, likes, popular_order, is_reply)
    VALUES (%s, %s, %s, %s, %s, %s)
                """, (video_id, row.text, row.writting_date, row.likes,
                      count if in_popular_order else 2147483646, row.is_reply))
                count += 1


def delete_comments(video_id: str):
    """Удалить **все** комментарии под видео"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
DELETE FROM public.commentary
    WHERE url = %s
                """, (video_id,))
