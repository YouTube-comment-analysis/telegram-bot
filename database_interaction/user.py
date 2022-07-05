import enum
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


class UserCabinet:
    """Класс, хранящий информацию о пользователе"""

    def __init__(self, user_id: int, first_name: str, last_name: str, middle_name: str, phone: str, email: str,
                 credits: int):
        self.user_id = user_id
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
SELECT user_id, credits, email, first_name, last_name, middle_name, phone
    FROM public.cabinet
    WHERE user_id = %s
            """, (user_id,))
            data = curs.fetchone()
            return UserCabinet(
                user_id=data[0],
                credits=data[1],
                email=data[2],
                first_name=data[3],
                last_name=data[4],
                middle_name=data[5],
                phone=data[6],
            )


def update_user_credits(user_id: int, new_value: int):
    """Обновить кредиты у пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
UPDATE public.cabinet
    SET credits = %s
    WHERE user_id = %s;
            """, (new_value, user_id))


# tested
def user_exists(user_id: int) -> bool:
    """Проверка зарегистрирован ли пользователь в базе"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT EXISTS(
    SELECT * FROM public.cabinet
        WHERE user_id = %s
)
            """, (user_id,))
            return curs.fetchone()[0]
