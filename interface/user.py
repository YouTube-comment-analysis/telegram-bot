from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog import Dialog, Window, DialogManager

import config
from authorization_process.auth import get_authed_user_id, change_password
from database_interaction.promocode import use_promocode
from database_interaction.user import get_user_cabinet, get_user_role

bot = Bot(token=config.telegram_bot_token)


class DialogUser(StatesGroup):
    home_page = State()
    personal_area = State()
    activate_promo = State()
    input_old_passw = State()
    input_new_passw = State()

    # analysis_video = State()
    # analysis_channel = State()
    # favorites_video = State()
    # favorites_channel = State()
    # view_all_video = State()
    # view_all_channel = State()
    # add_video_in_favorites = State()
    # delete_video_in_favorites = State()
    # add_channel_in_favorites = State()
    # delete_channel_in_favorites = State()
    # history_video = State()
    # view_all_video_in_history = State()
    # history_channel = State()
    # view_all_channel_in_history = State()


async def to_personal_area(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.personal_area)


async def get_data_personal_area(dialog_manager: DialogManager, **kwargs):
    telegram_id = dialog_manager.event.from_user.id
    user_id = get_authed_user_id(telegram_id)[1]
    user_personal_area = get_user_cabinet(user_id)
    user_role = get_user_role(user_id).name
    # dialog_data = dialog_manager.current_context().dialog_data
    return {
        "role": user_role,
        "name": user_personal_area.first_name,
        "surname": user_personal_area.last_name,
        "patronymic": user_personal_area.middle_name,
        "email": user_personal_area.email,
        "phone": user_personal_area.phone,
        "credits": user_personal_area.credits,
    }


async def to_activate_promo(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.activate_promo)


async def promo_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    if use_promocode(get_authed_user_id(m.from_user.id)[1], m.text)[0]:
        await m.answer(f"Ваша энергия успешно пополнена!")
        await manager.dialog().switch_to(DialogUser.personal_area)
    else:
        await m.answer(f"Неверный промокод.")
        await manager.dialog().switch_to(DialogUser.activate_promo)


async def to_cancel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.personal_area)


async def to_change_passw(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.input_old_passw)


old_passw = None


async def input_old_passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    global old_passw
    old_passw = m.text
    await manager.dialog().switch_to(DialogUser.input_new_passw)


async def input_new_passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    if change_password(m.from_user.id, old_passw, m.text):
        await m.answer(f"Пароль изменен!")
        await manager.dialog().switch_to(DialogUser.personal_area)
    else:
        await m.answer(f"Вы неправильно ввели ваш старый пароль.")
        await manager.dialog().switch_to(DialogUser.input_old_passw)


async def to_back(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.home_page)


dialog_user = Dialog(
    Window(
        Const("Добро пожаловать на главую страницу!"),
        Button(Const("Личный кабинет"), id="personal_area", on_click=to_personal_area),
        # Button(Const("Проанализировать"), id="analyze", on_click=to_analyze),
        # Button(Const("Избранное"), id="favorites", on_click=to_favorites),
        # Button(Const("Помощь"), id="help", on_click=to_help),
        # Button(Const("История"), id="history", on_click=to_history),
        # Button(Const("Выход"), id="exit", on_click=to_exit),
        state=DialogUser.home_page,
    ),
    Window(
        Format(
            "Личный кабинет."
            "\nРоль: {role}"
            "\nИмя: {name}"
            "\nФамилия: {surname}"
            "\nОтчество: {patronymic}"
            "\nЭлектронная почта: {email}"
            "\nНомер телефона: {phone}"
            "\nКоличество энергии: {credits}"),
        Button(Const("Активировать промокод"), id="activate_promo", on_click=to_activate_promo),
        Button(Const("Изменить пароль"), id="change_passw", on_click=to_change_passw),
        Button(Const("Назад"), id="back", on_click=to_back),
        state=DialogUser.personal_area,
        getter=get_data_personal_area,
    ),
    Window(
        Const("Введите номер промокода."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(promo_handler),
        state=DialogUser.activate_promo,
    ),
    Window(
        Const("Для того, чтобы изменить пароль, введите старый пароль."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(input_old_passw_handler),
        state=DialogUser.input_old_passw,
    ),
    Window(
        Const("Теперь введите ваш новый пароль."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(input_new_passw_handler),
        state=DialogUser.input_new_passw,
    )
    # Window(
    #     Const("Осталось ввести вашу электронную почту."),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(email_handler),
    #     state=DialogSign.input_email,
    # ),
    # Window(
    #     Const("Введите ваш логин."),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(log_handler),
    #     state=DialogSign.input_log,
    # ),
    # Window(
    #     Const("Введите ваш пароль"),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(passw_handler),
    #     state=DialogSign.input_passw,
    # ),
    # Window(
    #     Const("Повторите введенный пароль."),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(return_password_handler),
    #     state=DialogSign.return_input_passw,
    # ),
    # Window(
    #     Const("Ваша регистрация завершена!"),
    #     Button(Const("ОК"), id="ok", on_click=to_ok),
    #     state=DialogSign.registration_status,
    # ),
    # Window(
    #     Const("Введите логин."),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(login_handler),
    #     state=DialogSign.input_login,
    # ),
    # Window(
    #     Const("Введите пароль."),
    #     Button(Const("Отмена"), id="cancel", on_click=to_cancel),
    #     MessageInput(password_handler),
    #     state=DialogSign.input_password,
    # ),
    # Window(
    #     Const("Вход выполнен!"),
    #     Button(Const("ОК"), id="ok", on_click=to_ok),
    #     state=DialogSign.login_status,
    # )
)
