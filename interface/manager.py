from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import Message
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto

from database_interaction.auth import get_login_exists, get_user_id
from database_interaction.user import add_user_credits
from interface.FSM import DialogUser, DialogMngr


async def to_user_mode(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogUser.home_page)


async def to_start(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogMngr.start)


async def to_give_energy(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogMngr.get_login_to_give_energy)


login_to_give_enegry = None


async def input_login_to_give_enegry_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                             manager: DialogManager):
    if get_login_exists(m.text):
        global login_to_give_enegry
        login_to_give_enegry = m.text
        await manager.dialog().switch_to(DialogMngr.give_energy)
    else:
        await m.answer(f"Пользователя с логином: {m.text} - не существует.")
        await manager.dialog().switch_to(DialogMngr.get_login_to_give_energy)


async def input_give_enegry_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                       manager: DialogManager):
    add_user_credits(get_user_id(login_to_give_enegry), int(m.text))
    await m.answer(f"Пользователю под логином: {login_to_give_enegry} начислено {m.text} энергии.")
    await manager.dialog().switch_to(DialogMngr.start)


dialog_manager = Dialog(
    Window(
        Format("Личный кабинет менеджера"),
        Button(Const("Выдать энергию"), id="change_passw", on_click=to_give_energy),
        Button(Const("ЮзерМод"), id="user_mode", on_click=to_user_mode),
        state=DialogMngr.start,
    ),
    Window(
        Format("Кому хотите выдать энергию? Введите логин"),
        Button(Const("Назад"), id="back", on_click=to_start),
        MessageInput(input_login_to_give_enegry_handler),
        state=DialogMngr.get_login_to_give_energy,
    ),
    Window(
        Format("Какое количество энергии выдать пользователю?"),
        Button(Const("Назад"), id="back", on_click=to_start),
        MessageInput(input_give_enegry_handler),
        state=DialogMngr.give_energy,
    )
)
