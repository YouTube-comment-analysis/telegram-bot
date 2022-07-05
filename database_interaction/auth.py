from typing import Tuple

from database_interaction.db_connection import connection
from database_interaction.user import UserRole, UserCabinet


def get_password(login: str) -> tuple[bytes, bytes]:
    """
    Получить два значения зашифрованного пароля
    :return: salt, pwd_hash
    """
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
    SELECT pwd_salt, pwd_hash
    FROM public.authorization
        WHERE login = %s
            """, (login,))
            data = curs.fetchone()
            return data[0], data[1]


def get_login_exists(login: str) -> bool:
    """Проверить зарегистрирован ли пользователь с таким логином"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT EXISTS(
    SELECT *
    FROM public.authorization
        WHERE login = %s
)
            """, (login,))
            return curs.fetchone()[0]


def get_user_id(login: str) -> int:
    """Получить user_id пол логину пользователя. **Только при успешной авторизации**"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
SELECT user_id
FROM public.authorization
    WHERE login = %s
                    """, (login,))
            return curs.fetchone()[0]


def insert_user_auth_data(user_id: int, login: str, pwd_salt: bytes, pwd_hash: bytes):
    """Загрузить в базу логин, зашифрованный пароль пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.authorization(
    login, pwd_salt, pwd_hash, user_id)
    VALUES (%s, %s, %s, %s);
                """, (login, pwd_salt, pwd_hash, user_id))


def change_password(user_id: int, pwd_salt: bytes, pwd_hash: bytes):
    """Изменить пароль существующего, авторизованного пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
UPDATE public.authorization
SET pwd_salt = %s,
    pwd_hash = %s
WHERE
    user_id = %s
            """, (pwd_salt, pwd_hash, user_id))


def create_user_and_cabinet(role: UserRole, user: UserCabinet) -> int:
    """Зарегистрировать пользователя"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
INSERT INTO public.users(
    enter_date, role_name)
    VALUES (current_timestamp, %s)
    RETURNING user_id
            """, (role.value,))
            user_id: int = curs.fetchone()[0]
            curs.execute("""
INSERT INTO public.cabinet(
    user_id, credits, email, first_name, last_name, middle_name, phone)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, user.credits, user.email,
                  user.first_name, user.last_name, user.middle_name, user.phone))
            return user_id
