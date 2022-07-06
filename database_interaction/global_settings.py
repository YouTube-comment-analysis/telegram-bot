import enum

from database_interaction.db_connection import connection


class Settings(enum.Enum):
    max_comments = 'max_comments_from_video'


def get_global_setting(setting: Settings) -> int:
    """Получить значение глобальной настройки"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute(f"""
SELECT value
FROM public.global_settings
WHERE setting = %s
            """, (setting.value,))
            return curs.fetchone()[0]


def set_global_setting(setting: Settings, new_value: int):
    """Установить значение глобальной настройки"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
UPDATE public.global_settings
    SET value = %s
    WHERE setting = %s;
            """, (new_value, setting.value))