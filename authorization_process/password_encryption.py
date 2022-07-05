from typing import Tuple
import os
import hashlib
import hmac

import psycopg2

import config


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Хэширование пароля
    :param password: str
    Пароль пользователя
    :return:
    salt - добавка для шифрования пароля, pw_hash - хэш код пароля
    """
    salt = os.urandom(config.encrypt_settings['salt_length'])
    pw_hash = hashlib.pbkdf2_hmac(config.encrypt_settings['hash_name'], password.encode(), salt,
                                  config.encrypt_settings['iterations'])
    return salt, pw_hash


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac(config.encrypt_settings['hash_name'], password.encode(), salt,
                            config.encrypt_settings['iterations'])
    )
