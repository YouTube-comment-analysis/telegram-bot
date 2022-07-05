import database_interaction.auth as auth
import database
from authorization_process.password_encryption import is_correct_password, hash_new_password

user = database.user.UserCabinet
role = database.user.UserRole


def sign_up(
        user_cabinet: user,
        user_role: role,
        login: str,
        password: str
        ) -> int:
    """
    Регистрация пользователя в базе
    :return: user_id, уникальный идентификатор пользователя
    """
    user_id = auth.create_user_and_cabinet(user_role, user_cabinet)
    pwd_salt, pwd_hash = hash_new_password(password)
    auth.insert_user_auth_data(user_id, login, pwd_salt, pwd_hash)
    return user_id


def sign_in(login: str, password: str) -> tuple[bool, int]:
    """
    Авторизация пользователя
    :return:
    При верных данных возвращается [True, user_id], при неверных [False, 0]
    """
    pwd = auth.get_password(login)
    check = is_correct_password(pwd[0], pwd[1], password)
    return (True, auth.get_user_id(login)) if check else (False, 0)