from database_interaction.db_connection import connection
from database_interaction.user import add_user_credits


def use_promocode(user_id: int, promocode: str) -> tuple[bool, int]:
    """
    Использовать промокод и зачислить кредиты на счет пользователя
    :return В случае правильного прокомокда вернутся начисленные кредиты [True, credits],
            в случае неправильного или уже использованного [False, 0]
    """
    with connection as connect:
        with connect.cursor() as curs:
            # проверить промокод на подлинность
            curs.execute("""
SELECT EXISTS(
    SELECT * FROM public.promocode
    WHERE promocode_key = %s AND NOT is_used
)
            """, (promocode,))
            valid = curs.fetchone()[0]

    if not valid:
        return False, 0
    else:
        with connection as connect:
            with connect.cursor() as curs:
                # получаем кредиты в промокоде
                curs.execute("""
SELECT credits_value FROM public.promocode
WHERE promocode_key = %s
                """, (promocode,))
                promo_credits = curs.fetchone()[0]
        # начислить кредиты
        add_user_credits(user_id, promo_credits)
        # пометить промокод как использованный
        with connection as connect:
            with connect.cursor() as curs:
                curs.execute("""
        UPDATE public.promocode
        SET is_used = true
        WHERE promocode_key = %s
                """, (promocode,))
        return True, promo_credits
