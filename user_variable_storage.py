import enum

from comment_scrapping.comment import Comment

"""
    Хранилище всех загруженных массивов
    telegram_id -> dict -> variables
"""

storage = dict()


class UserVariable(enum.Enum):
    comments_array = 'comments_array'
    a = 'b'
    b = 'c'


def add_variable_in_dict(telegram_id: int, variable: UserVariable, value):
    """
    Добавить глобальную переменную по телеграм id
    :param telegram_id: телеграм id
    :param variable: имя переменной
    :param value: значение переменной
    """
    storage[telegram_id][variable.value] = value


def get_variable_from_dict(telegram_id: int, variable: UserVariable):
    """
    Возвращает глобальную переменную по телеграм id
    :param telegram_id: телеграм id
    :param variable: имя переменной
    :return: значение переменной
    """
    return storage[telegram_id][variable.value]


add_variable_in_dict(1234, UserVariable.a, ['a', 'b'])
print(get_variable_from_dict(1234, UserVariable.a))
