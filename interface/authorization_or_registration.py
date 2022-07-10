from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.types import Message, CallbackQuery

import authorization
from authorization_process.auth import sign_in, sign_up
from database_interaction.auth import get_login_exists
from database_interaction.user import UserCabinet, UserRole
from aiogram_dialog import Dialog, DialogManager, Window, StartMode

from interface.FSM import DialogSign, DialogUser
from check_input_data import CheckInputData

info = UserCabinet("Пусто", "Пусто", "Пусто", "Пусто", "Пусто", 5)
login = None
password = None
return_password = None


async def to_sign_up(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogSign.input_name)


async def name_handler(m: Message, dialog: ManagedDialogAdapterProto,
                       manager: DialogManager):
    if CheckInputData.russian_chars(m.text):
        info.first_name = m.text
        await m.answer(f"Приятно познакомиться, {m.text}.")
        await dialog.next()
    else:
        await m.answer(f"Можно вводить только русские символы. Первая буква - заглавная, а здесь что то не так - {m.text}.")
        await dialog.switch_to(DialogSign.input_name)


async def surname_handler(m: Message, dialog: ManagedDialogAdapterProto,
                          manager: DialogManager):
    if CheckInputData.russian_chars(m.text):
        info.last_name = m.text
        await dialog.next()
    else:
        await m.answer(f"Можно вводить только русские символы. Первая буква - заглавная, а здесь что то не так - {m.text}.")
        await dialog.switch_to(DialogSign.input_surname)


async def patronymic_handler(m: Message, dialog: ManagedDialogAdapterProto,
                             manager: DialogManager):
    if CheckInputData.russian_chars(m.text):
        info.middle_name = m.text
        await dialog.next()
    else:
        await m.answer(f"Можно вводить только русские символы. Первая буква - заглавная, а здесь что то не так - {m.text}.")
        await dialog.switch_to(DialogSign.input_patronymic)


async def phone_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    if CheckInputData.phone_number(m.text):
        info.phone = m.text
        await dialog.next()
    else:
        await m.answer(f"Номер телефона должен вводиться с 79_________ , а здесь что то не так - {m.text}.")
        await dialog.switch_to(DialogSign.input_phone)


async def email_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    if CheckInputData.email(m.text):
        info.email = m.text
        await dialog.next()
    else:
        await m.answer(f"Пример правильной почты xxxx@domen.com , а здесь что то не так - {m.text}.")
        await dialog.switch_to(DialogSign.input_email)


async def to_sign_in(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogSign.input_login_auth)


# Для входа
async def login_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    if get_login_exists(m.text):
        global login
        login = m.text
        await dialog.next()
    else:
        await m.answer(f"Ваш логин: {m.text} - неверный.")
        await manager.dialog().switch_to(DialogSign.input_login_auth)


# Для входа
async def password_handler(m: Message, dialog: ManagedDialogAdapterProto,
                           manager: DialogManager):
    if sign_in(login, m.text, m.from_user.id):
        await dialog.next()
    else:
        await m.answer("Что-то пошло не так...\nВозможные проблемы:\nваш пароль неверный\nпользователь уже онлайн.")
        await manager.dialog().switch_to(DialogSign.input_password_auth)


# Для регистрации
async def log_handler(m: Message, dialog: ManagedDialogAdapterProto,
                      manager: DialogManager):
    if not get_login_exists(m.text):
        global login
        login = m.text
        await dialog.next()
    else:
        await m.answer("Пользователь с таким логином уже существует.")
        await manager.dialog().switch_to(DialogSign.input_log_reg)


# Для регистрации
async def passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    global password
    password = m.text
    await dialog.next()


# Для регистрации
async def return_password_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    if m.text == password:
        global return_password
        return_password = m.text
        sign_up(info, UserRole.user, login, return_password)
        sign_in(login, m.text, m.from_user.id)
        await dialog.next()
    else:
        await m.answer("Что-то пошло не так.. Ваш повторный пароль не совпадает с предыдущим.")
        await manager.dialog().switch_to(DialogSign.input_passw_reg)


async def to_ok(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogUser.home_page)


async def to_cancel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogSign.start)


# async def go_next(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().next()


dialog_start = Dialog(
    Window(
        Const(
            "Приветствую гость! Вам необходимо зарегистрироваться/войти в систему. \nИначе вы не сможете пользоваться функциями бота"),
        Button(Const("Зарегистрироваться"), id="sign_up", on_click=to_sign_up),
        Button(Const("Войти"), id="sign_in", on_click=to_sign_in),
        state=DialogSign.start,
    ),
    Window(
        Const("Введите ваше имя."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(name_handler),
        state=DialogSign.input_name,
    ),
    Window(
        Const("Теперь введите вашу фамилию."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(surname_handler),
        state=DialogSign.input_surname,
    ),
    Window(
        Const("Теперь введите ваше отчество."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(patronymic_handler),
        state=DialogSign.input_patronymic,
    ),
    Window(
        Const("Теперь введите ваш номер телефона.\nПожалуйста используйте данный формат: 79123456789"),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(phone_handler),
        state=DialogSign.input_phone,
    ),
    Window(
        Const("Осталось ввести вашу электронную почту."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(email_handler),
        state=DialogSign.input_email,
    ),
    Window(
        Const("Введите ваш логин."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(log_handler),
        state=DialogSign.input_log_reg,
    ),
    Window(
        Const("Введите ваш пароль"),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(passw_handler),
        state=DialogSign.input_passw_reg,
    ),
    Window(
        Const("Повторите введенный пароль."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(return_password_handler),
        state=DialogSign.return_input_passw_reg,
    ),
    Window(
        Const("Ваша регистрация завершена!"),
        Button(Const("ОК"), id="okey", on_click=to_ok),
        state=DialogSign.registration_status,
    ),
    Window(
        Const("Введите логин."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(login_handler),
        state=DialogSign.input_login_auth,
    ),
    Window(
        Const("Введите пароль."),
        Button(Const("Отмена"), id="cancel", on_click=to_cancel),
        MessageInput(password_handler),
        state=DialogSign.input_password_auth,
    ),
    Window(
        # TODO: убрать это
        Const("Вход выполнен!"),
        Button(Const("ОК"), id="okey", on_click=to_ok),
        state=DialogSign.login_status,
    )
)


async def start(m: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    authorization.sign_out(m.from_user.id)
    await dialog_manager.start(DialogSign.start, mode=StartMode.RESET_STACK)
