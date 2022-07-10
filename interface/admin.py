from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from interface.FSM import DialogUser, DialogAdmin


async def to_user_mode(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogUser.home_page)


dialog_admin = Dialog(
    Window(
        Format("Личный кабинет администратора"),
        # Button(Const("Получение статистики о новых пользователях за период"), id="activate_promo", on_click=to_activate_promo),
        # Button(Const("Получение статистики посещаемости"), id="change_passw", on_click=to_change_passw),
        # Button(Const("Настроить макс. кол-во комментариев для скачивания"), id="back_in_home_page", on_click=to_back_in_home_page),
        # Button(Const("Просмотр статистики по хранимым в БД данным"), id="back_in_home_page",on_click=to_back_in_home_page),
        # Button(Const("Выдать/отнять права доступа"), id="change_passw", on_click=to_change_passw),
        Button(Const("ЮзерМод"), id="user_mode", on_click=to_user_mode),
        state=DialogAdmin.start,
    )
)
