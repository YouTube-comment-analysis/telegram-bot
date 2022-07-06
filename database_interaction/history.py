from datetime import datetime
from database_interaction.db_connection import connection


class ChannelHistory:
    def __init__(self, user_id: int, channel_id: str, viewing_date: datetime):
        self.user_id = user_id
        self.channel_id = channel_id,
        self.viewing_date = viewing_date


def get_all_channel_history() -> [ChannelHistory]:
    """Получить весь список истории по анализу каналов у всех пользователей"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
    SELECT
    user_id, channel_url, viewing_date
    FROM
    public.history_channel;
    ORDER BY viewing_date DESC
                """,)
            return map(lambda x: ChannelHistory(x['user_id'], x['channel_url'], x['viewing_date']), curs)


def get_user_channel_history(user_telegram_id: int, limited: bool = False):
    """Получить список истории по анализу канала у одного пользователя, можно ограничить выборку десятью первыми элементами"""
    with connection as connect:
        with connect.cursor() as curs:
            curs.execute("""
    SELECT
    user_id, channel_url, viewing_date
    FROM
    public.history_channel
    WHERE user_id = %s
    ORDER BY viewing_date DESC
                """, (user_telegram_id,))
            result = map(lambda x: ChannelHistory(x['user_id'], x['channel_url'], x['viewing_date']), curs)
            return result[:10] if limited else result



