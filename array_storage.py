from comment_scrapping.comment import Comment

"""
    Хранилище всех загруженных массивов
    telegram_id -> comments[Comment]
"""

storage = dict()


def check_arr_in_storage(telegram_id: str):
    """Проверить скачаны ли комментарии у пользователя"""
    return telegram_id in storage


def get_comments_array(telegram_id: str):
    """Получить уже скачанный массив комментариев"""
    if check_arr_in_storage(telegram_id):
        return storage[telegram_id]


def add_arr_to_storage(telegram_id: str, comments: [Comment]):
    """Добавить массив на хранение"""
    if not check_arr_in_storage(telegram_id):
        storage[telegram_id] = [comments, 0]


def drop_arr_from_storage(telegram_id: str):
    """Удаляет массив из памяти"""
    if check_arr_in_storage(telegram_id):
        storage.pop(telegram_id)


