import enum

from comment_scrapping.comment import Comment

"""
    Хранилище всех загруженных массивов
    telegram_id -> dict -> variables
"""

storage = dict()


class UserVariable(enum.Enum):
    comments_array = 'comments_array'
    comment_total_count = 'comment_total_count'
    download_time_sec = 'download_time_sec'
    old_passw = 'old_passw'
    popular_or_no = 'popular_or_no' # 1 - по популярности, '2' - по времени
    investment_or_not = 'investment_or_not' # 1 - учитывать вложение, 2 - не учитывать вложение
    analysis_first_date_selected = 'analysis_first_date_selected'
    analysis_second_date_selected = 'analysis_second_date_selected'
    input_url = "input_url"
    login = "login"
    password = "password"
    return_password = "return_password"
    first_name = 'first_name'
    last_name = 'last_name'
    middle_name = 'middle_name'
    phone = 'phone'
    email = 'email'
    is_stop_download_comments = 'is_stop_download_comments'
    type_of_grouping = 'type_of_grouping' #'day' (1); 'week' (2); 'month' (3)
    is_url_video = 'is_url_video'
    list_of_videos = 'list_of_videos'
    is_order_matter = 'is_order_matter'
    is_in_loop = 'is_in_loop'
    is_chart_pie = 'is_chart_pie'
    current_date_interval_state = 'current_date_interval_state' #0 - интервал на канале; 1 - интервал на диаграмме; 2 - интервал на сентименте
    user_login_in_admin_mode = 'user_login_in_admin_mode'
    phrases = 'phrases'


def try_add_new_telegram_id(telegram_id: str):
    '''
    Вызови этот метод при заходе пользователя (start). Он добавляет пространство глобальных переменных для пользователя
    :param telegram_id:
    '''
    if telegram_id not in storage:
        storage[telegram_id] = dict()


def delete_user_variables(telegram_id: str):
    '''
    ви этот метод при выходе пользователя (to_yes). Он удаляет пространство глобальных переменных пользователя
    :param telegram_id:
    '''
    storage.pop(telegram_id, None)


def add_variable_in_dict(telegram_id: str, variable: UserVariable, value):
    """
    Добавить глобальную переменную по телеграм id
    :param telegram_id: телеграм id
    :param variable: имя переменной
    :param value: значение переменной
    """
    storage[telegram_id][variable.value] = value


def get_variable_from_dict(telegram_id: str, variable: UserVariable):
    """
    Возвращает глобальную переменную по телеграм id
    :param telegram_id: телеграм id
    :param variable: имя переменной
    :return: значение переменной
    """
    return storage[telegram_id][variable.value]

