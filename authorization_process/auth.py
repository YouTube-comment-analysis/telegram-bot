import database_interaction.auth as auth
import database
from authorization_process.password_encryption import is_correct_password, hash_new_password

user = database.user.UserCabinet
role = database.user.UserRole

authorized_users = dict()


def sign_up(
        user_cabinet: user,
        user_role: role,
        login: str,
        password: str
        ):
    """Регистрация пользователя в базе"""
    user_id = auth.create_user_and_cabinet(user_role, user_cabinet)
    pwd_salt, pwd_hash = hash_new_password(password)
    auth.insert_user_auth_data(user_id, login, pwd_salt, pwd_hash)


def sign_in(login: str, password: str, telegram_id: int) -> bool:
    """
    Авторизация пользователя
    :param telegram_id: id пользователя в telegram, для определения пользователя,
    под которым авторизован клиент в системе
    :return:
    При верных данных возвращается [True, user_id], при неверных [False, 0]
    """
    pwd = auth.get_password(login)
    check = is_correct_password(pwd[0], pwd[1], password)
    if not check:
        return False
    else:
        user_id = auth.get_user_id(login)
        if user_id not in authorized_users.values():
            authorized_users[telegram_id] = user_id
            return True
        else:
            return False


def sign_out(telegram_id: int):
    """
    Выход из системы
    :return Успех операции: True - вышел успешно, False - не был авторизован
    """
    if telegram_id in authorized_users:
        authorized_users.pop(telegram_id)
        return True
    else:
        return False


def check_auth(telegram_id: int):
    return telegram_id in authorized_users


def get_authed_user_id(telegram_id: int) -> tuple[bool, int]:
    if check_auth(telegram_id):
        return True, authorized_users[telegram_id]
    else:
        return False, 0


def change_password(telegram_id: int, old_password: str, new_password: str) -> bool:
    """
    Смена пароля у пользователя
    :return Успех операции
    """
    authed, user_id = get_authed_user_id(telegram_id)
    if authed:
        old_salt, old_pwd_hash = auth.get_password(auth.get_user_login(user_id))
        if is_correct_password(old_salt, old_pwd_hash, old_password):
            new_salt, new_pwd_hash = hash_new_password(new_password)
            auth.change_password(user_id, new_salt, new_pwd_hash)
            return True
    return False


