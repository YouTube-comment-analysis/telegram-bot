import enum

from database_interaction import auth
from database_interaction.db_connection import connection

class UserRole(enum.Enum):
    banned = 'ban'
    admin = 'admin'
    user = 'user'
    manager = 'manager'


# tested
def get_user_role(user_id: int):
    """Получить роль пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT user_id, enter_date, role_name
    FROM public.users
    WHERE user_id = %s
            """, (user_id,))
            data = curs.fetchone()
            return UserRole(data[2])


def set_user_role(login: str, role: UserRole):
    if auth.get_login_exists(login):
        user_id = auth.get_user_id(login)

        """Изменить роль пользователя"""
        with connection as connect:
            with connect.cursor() as curs:
                curs.execute("""
UPDATE public.users
SET role_name=%s
WHERE user_id = %s;
                """, (role.value, user_id))
                data = curs.fetchone()
                return UserRole(data[2])


class UserCabinet:
    """Класс, хранящий информацию о пользователе"""

    def __init__(self, first_name: str, last_name: str, middle_name: str, phone: str, email: str,
                 credits: int):
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.phone = phone
        self.email = email
        self.credits = credits


# tested
def get_user_cabinet(user_id: int) -> UserCabinet:
    """Получить данные из личного кабинета"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT credits, email, first_name, last_name, middle_name, phone
    FROM public.cabinet
    WHERE user_id = %s
            """, (user_id,))
            data = curs.fetchone()
            return UserCabinet(
                credits=data[0],
                email=data[1],
                first_name=data[2],
                last_name=data[3],
                middle_name=data[4],
                phone=data[5],
            )


def get_user_credits(user_id: int):
    """Получить текущие кредиты пользователя"""
    return get_user_cabinet(user_id).credits


def add_user_credits(user_id: int, addition: int):
    """Добавить кредиты пользователю"""
    user_credits = get_user_credits(user_id)
    update_user_credits(user_id, user_credits + addition)


def decrease_user_credits(user_id: int, decrease: int) -> bool:
    """
    Забрать кредиты у пользователя
    :param decrease кредиты должны быть > 0
    :return Возвращается успех операции True - успешно, False - недостаточно кредитов
    """
    if decrease < 0:
        raise 'кредиты должны быть > 0'

    user_credits = get_user_credits(user_id)
    if user_credits - decrease <= 0:
        return False
    else:
        update_user_credits(user_id, user_credits - decrease)
        return True


def update_user_credits(user_id: int, new_value: int):
    """Обновить кредиты у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
UPDATE public.cabinet
    SET credits = %s
    WHERE user_id = %s;
            """, (new_value, user_id))



