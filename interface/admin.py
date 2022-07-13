from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from interface.user.user_variable_storage import UserVariable, add_variable_in_dict, get_variable_from_dict

from authorization_process import authorization
from interface.FSM import DialogUser, DialogAdmin
from database_interaction import database
from database_interaction.user import UserRole


async def input_user_login(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    if authorization.get_login_exists(m.text):
        add_variable_in_dict(m.from_user.id, UserVariable.user_login_in_admin_mode, m.text)
        await manager.dialog().switch_to(DialogAdmin.role_changer)
    else:
        await m.reply("Такого логина не сусществует :(")
        await manager.dialog().switch_to(DialogAdmin.input_login)


async def input_role(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    text = m.text
    user_login = get_variable_from_dict(m.from_user.id, UserVariable.user_login_in_admin_mode)
    if text.lower() == 'админ':
        database.user.set_user_role(user_login, UserRole.admin)
        await m.reply("Успешно!")
        await manager.dialog().switch_to(DialogAdmin.start)
    elif text.lower() == 'менеджер':
        database.user.set_user_role(user_login, UserRole.manager)
        await m.reply("Успешно!")
        await manager.dialog().switch_to(DialogAdmin.start)
    elif text.lower() == 'пользователь':
        database.user.set_user_role(user_login, UserRole.user)
        await m.reply("Успешно!")
        await manager.dialog().switch_to(DialogAdmin.start)
    else:
        await m.reply("Не понимаю...")
        await manager.dialog().switch_to(DialogAdmin.role_changer)


async def input_login_analysis(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    if authorization.get_login_exists(m.text):
        add_variable_in_dict(m.from_user.id, UserVariable.user_login_in_admin_mode, m.text)
        await manager.dialog().switch_to(DialogAdmin.user_statistic)
    else:
        await m.reply("Такого логина не существует :(")
        await manager.dialog().switch_to(DialogAdmin.input_login_analysis)


async def input_max_comments(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    if m.text.isdigit() and int(m.text) > 0:
        database.global_settings.set_global_setting(
            database.global_settings.Settings.max_comments, int(m.text)
        )
        await m.reply("Успешно!")
        await manager.dialog().switch_to(DialogAdmin.start)
    else:
        await m.reply("Что?")
        await manager.dialog().switch_to(DialogAdmin.input_max_comment_setting)


async def user_analysis(dialog_manager: DialogManager, **kwargs):
    login = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.user_login_in_admin_mode)
    user_video_requests = [
        database.history.get_user_video_requests_count_for_last_parameter('1 day', login),
        database.history.get_user_video_requests_count_for_last_parameter('7 day', login),
        database.history.get_user_video_requests_count_for_last_parameter('1 month', login)
    ]
    user_channel_requests = [
        database.history.get_user_channel_requests_count_for_last_parameter('1 day', login),
        database.history.get_user_channel_requests_count_for_last_parameter('7 day', login),
        database.history.get_user_channel_requests_count_for_last_parameter('1 month', login)
    ]
    temp = f"""
         Количество запросов анализа видео:
            За день: {user_video_requests[0]}
            За неделю: {user_video_requests[1]}
            За месяц: {user_video_requests[2]}
         Количество запросов анализа каналов:
            За день: {user_channel_requests[0]}
            За неделю: {user_channel_requests[1]}
            За месяц: {user_channel_requests[2]}
         """
    return {'text': temp}


async def get_all_users_stat(dialog_manager: DialogManager, **kwargs):
    new_users_info = [
        database.history.get_new_users_count_for_last_parameter('1 day'),
        database.history.get_new_users_count_for_last_parameter('7 day'),
        database.history.get_new_users_count_for_last_parameter('1 month')
    ]
    users_video_requests = [
        database.history.get_new_users_count_for_last_parameter('1 day'),
        database.history.get_new_users_count_for_last_parameter('7 day'),
        database.history.get_new_users_count_for_last_parameter('1 month')
    ]
    users_channel_requests = [
        database.history.get_channel_requests_count_for_last_parameter('1 day'),
        database.history.get_channel_requests_count_for_last_parameter('7 day'),
        database.history.get_channel_requests_count_for_last_parameter('1 month')
    ]
    temp = f"""
         Количество новых пользователей:
            За день: {new_users_info[0]}
            За неделю: {new_users_info[1]}
            За месяц: {new_users_info[2]}
         Количество запросов анализа видео:
            За день: {users_video_requests[0]}
            За неделю: {users_video_requests[1]}
            За месяц: {users_video_requests[2]}
         Количество запросов анализа каналов:
            За день: {users_channel_requests[0]}
            За неделю: {users_channel_requests[1]}
            За месяц: {users_channel_requests[2]}
         """
    return {'text': temp}


async def to_user_mode(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogUser.home_page)


async def to_admin_statistics(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.statistics)


async def to_input_login_user_statistics(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.input_login_analysis)


async def to_role_changer(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.input_login)


async def to_user_statistics(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.statistics)


async def to_settings(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.input_max_comment_setting)


async def to_start(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogAdmin.start)


dialog_admin = Dialog(
    Window(
        Format("Личный кабинет администратора"),
        Button(Const("Получение статистики по пользователю"), id="get_admin_statistics",
               on_click=to_input_login_user_statistics),
        Button(Const("Настроить макс. кол-во комментариев для скачивания"), id="set_settings", on_click=to_settings),
        Button(Const("Просмотр статистики по запросам"), id="requests_stat", on_click=to_admin_statistics),  #
        Button(Const("Выдать/отнять права доступа"), id="change_role", on_click=to_role_changer),  #
        Button(Const("ЮзерМод"), id="user_mode", on_click=to_user_mode),  #
        state=DialogAdmin.start,
    ),
    Window(
        Format("Статистика:{text}"),
        Button(Const("Назад"), id="back", on_click=to_start),
        getter=get_all_users_stat,
        state=DialogAdmin.statistics,
    ),  #
    Window(
        Format("Введите логин пользователя"),
        Button(Const("Отмена"), id="back", on_click=to_start),
        MessageInput(input_user_login),
        state=DialogAdmin.input_login,
    ),  #
    Window(
        Format("Напишите новую роль:\nАдмин\nМенеджер\nПользователь"),
        Button(Const("Отмена"), id="back", on_click=to_start),
        MessageInput(input_role),
        state=DialogAdmin.role_changer,
    ),  #

    Window(
        Format("Введите логин пользователя"),
        Button(Const("Отмена"), id="back", on_click=to_start),
        MessageInput(input_login_analysis),
        state=DialogAdmin.input_login_analysis,
    ),
    Window(
        Format("Статистика пользователя:{text}"),
        Button(Const("Назад"), id="back", on_click=to_start),
        getter=user_analysis,
        state=DialogAdmin.user_statistic,
    ),
    Window(
        Format("Введите сколько максимально \nкомментариев можно скачать"),
        Button(Const("Отмена"), id="back", on_click=to_start),
        MessageInput(input_max_comments),
        state=DialogAdmin.input_max_comment_setting,
    ),
)
