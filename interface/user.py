from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.when import Whenable
from typing import Dict
import authorization
from authorization_process.auth import get_authed_user_id, change_password
from authorization_process.password_encryption import is_correct_password
from database_interaction.auth import get_password, get_user_login
from database_interaction.promocode import use_promocode
from database_interaction.user import get_user_cabinet, get_user_role, UserRole

import database

from interface.FSM import DialogSign, DialogUser, DialogAdmin, DialogMngr

"""Личный кабинет"""


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
    old_salt, old_pwd_hash = get_password(get_user_login(get_authed_user_id(m.from_user.id)[1]))
    if is_correct_password(old_salt, old_pwd_hash, m.text):
        global old_passw
        old_passw = m.text
        await manager.dialog().switch_to(DialogUser.input_new_passw)
    else:
        await m.answer(f"Вы неправильно ввели ваш старый пароль.")
        await manager.dialog().switch_to(DialogUser.input_old_passw)


async def input_new_passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    # if change_password(m.from_user.id, old_passw, m.text):
    change_password(m.from_user.id, old_passw, m.text)
    await m.answer(f"Пароль изменен!")
    await manager.dialog().switch_to(DialogUser.personal_area)
    # else:
    #     await m.answer(f"Вы неправильно ввели ваш старый пароль.")
    #     await manager.dialog().switch_to(DialogUser.input_old_passw)


async def to_back_in_home_page(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.home_page)


"""Избранное"""


async def to_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.favorites)


"""Избранное ВИДЕО"""


async def to_favorites_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.favorites_video)


async def get_data_last_ten_favorites_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    ten_favorites_video = list(map(lambda x: f"https://www.youtube.com/watch?v={x}",
                                   database.favorite.get_favorite_user_videos(user_id, True)))
    # # dialog_data = dialog_manager.current_context().dialog_data
    return {
        "text1": "У вас нет избранных видео." if len(ten_favorites_video) == 0 else "\n".join(ten_favorites_video),
    }


async def to_view_all_favorites_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.view_all_video_in_favorites)


async def get_data_favorites_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    data = database.favorite.get_favorite_user_videos(user_id, False)
    favorites_video = list(map(lambda x: f"https://www.youtube.com/watch?v={x}",
                               data))
    return {
        "text3": "У вас нет избранных видео." if len(favorites_video) == 0 else "\n".join(favorites_video),
    }


async def to_back_in_last_ten_favorites_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.favorites_video)


async def to_add_video_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.add_video_in_favorites)


async def input_url_video_to_add_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                              manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if "www.youtube.com/watch?v=" in url:
        id = url.split('watch?v=')[1]
        if id not in database.favorite.get_favorite_user_videos(user_id):
            database.favorite.add_favorite_user_video(user_id, id)
            await m.answer(f"Ваше видео добавлено в избранное!")
        else:
            await m.answer(f"Это видео уже есть в избранном.")
        await manager.dialog().switch_to(DialogUser.favorites_video)
    else:
        await m.answer(f"Это не похоже на ссылку с YouTube... ")
        await manager.dialog().switch_to(DialogUser.add_video_in_favorites)


async def to_delete_video_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.delete_video_in_favorites)


async def input_url_video_to_delete_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                 manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if "www.youtube.com/watch?v=" in url:
        id = url.split('watch?v=')[1]
        if id in database.favorite.get_favorite_user_videos(user_id):
            database.favorite.delete_favorite_user_video(user_id, id)
            await m.answer(f"Ваше видео из избранного удалено!")
            await manager.dialog().switch_to(DialogUser.favorites_video)
        else:
            await m.answer(f"Этого видео нет в вашем избранном... ")
            await manager.dialog().switch_to(DialogUser.delete_video_in_favorites)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.delete_video_in_favorites)


"""Избранные КАНАЛЫ"""


async def to_view_all_favorites_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.view_all_channel_in_favorites)


async def to_back_in_last_ten_favorites_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.favorites_channel)


async def to_favorites_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.favorites_channel)


# async def to_back_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.favorites)


async def get_data_last_ten_favorites_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    ten_favorites_channel = list(map(lambda x: f"https://www.youtube.com/c/{x}",
                                     database.favorite.get_favorite_user_channels(user_id, True)))
    return {
        "text2": "У вас нет избранных каналов." if len(ten_favorites_channel) == 0 else "\n".join(
            ten_favorites_channel),
    }


async def get_data_favorites_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    data = database.favorite.get_favorite_user_channels(user_id, False)
    favorites_channel = list(map(lambda x: f"https://www.youtube.com/watch?v={x}",
                                 data))
    return {
        "text4": "У вас нет избранных каналов." if len(favorites_channel) == 0 else "\n".join(favorites_channel),
    }


async def to_add_channel_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.add_channel_in_favorites)


async def to_delete_channel_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.delete_channel_in_favorites)


async def input_url_channel_to_add_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    # TODO: добавить проверку на user, channel в ссылку канала
    if "https://www.youtube.com/c/" in url:
        id = url.split('www.youtube.com/c/')[1]
        if id in database.favorite.get_favorite_user_channels(user_id):
            await m.answer(f"Этот канал уже в вашем избранном... ")
        else:
            database.favorite.add_favorite_user_channel(user_id, id)
            await m.answer(f"Ваш канал добавлен в избранное!")
        await manager.dialog().switch_to(DialogUser.favorites_channel)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.add_channel_in_favorites)


async def input_url_channel_to_delete_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                   manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if "https://www.youtube.com/c/" in url:
        id = url.split('www.youtube.com/c/')[1]
        if id in database.favorite.get_favorite_user_channels(user_id):
            database.favorite.delete_favorite_user_channel(user_id, id)
            await m.answer(f"Ваш канал удален из избранного!")
        else:
            await m.answer(f"Этого канала нет в вашем избранном... ")
        await manager.dialog().switch_to(DialogUser.favorites_channel)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.delete_channel_in_favorites)


"""История"""


async def to_history(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.history)


"""История ВИДЕО"""


async def get_data_history_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    history = database.history.get_user_video_history(user_id)
    return {
        "text7": "У вас нет видео в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
            Ссылка на видео: https://www.youtube.com/watch?v={x.url}
            Дата анализа: {x.viewing_date}
        """, history))),
    }


async def get_data_last_ten_history_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    history = database.history.get_user_video_history(user_id, True)
    return {
        "text5": "У вас нет видео в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
                Ссылка на видео: https://www.youtube.com/watch?v={x.url}
                Дата анализа: {x.viewing_date}
            """, history))),
    }


async def to_view_all_history_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.view_all_video_in_history)


async def to_history_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.history_video)


"""История КАНАЛОВ"""


async def to_history_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.history_channel)


async def to_view_all_history_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.view_all_channel_in_history)


async def get_data_history_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    history = database.history.get_user_channel_history(user_id)
    return {
        "text6": "У вас нет каналов в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
                Ссылка на канал: https://www.youtube.com/c/{x.channel_id}
                Дата анализа: {x.viewing_date}
            """, history))),
    }


async def get_data_last_ten_history_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    history = database.history.get_user_channel_history(user_id, True)
    return {
        "text8": "У вас нет каналов в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
                    Ссылка на канал: https://www.youtube.com/c/{x.channel_id}
                    Дата анализа: {x.viewing_date}
                """, history))),
    }


"""Помощь"""


async def to_help(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.help)


"""Выход"""


async def to_exit(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.exit)


async def to_yes(c: CallbackQuery, button: Button, manager: DialogManager):
    authorization.sign_out(manager.event.from_user.id)
    await manager.start(DialogSign.start)


"""Выход в админа"""


def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    user_id = get_authed_user_id(telegram_id)[1]
    return get_user_role(user_id) == UserRole.admin


async def to_admin(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogAdmin.start)


"""Выход в менеджера"""


def is_manager(data: Dict, widget: Whenable, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    user_id = get_authed_user_id(telegram_id)[1]
    return get_user_role(user_id) == UserRole.manager


async def to_manager(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(DialogMngr.start)


dialog_user = Dialog(
    Window(
        Const("Добро пожаловать на главую страницу!"),
        Button(Const("АдминМод"), id="admin", when=is_admin, on_click=to_admin),
        Button(Const("МенеджерМод"), id="manager", when=is_manager, on_click=to_manager),
        Button(Const("Личный кабинет"), id="personal_area", on_click=to_personal_area),
        # Button(Const("Проанализировать"), id="analyze", on_click=to_analyze),
        Button(Const("Избранное"), id="favorites", on_click=to_favorites),
        Button(Const("Помощь"), id="help", on_click=to_help),
        Button(Const("История"), id="history", on_click=to_history),
        Button(Const("Выход"), id="exit", on_click=to_exit),
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
        # TODO: редактирование информации пользователя
        Button(Const("Активировать промокод"), id="activate_promo", on_click=to_activate_promo),
        Button(Const("Изменить пароль"), id="change_passw", on_click=to_change_passw),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
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
    ),
    Window(
        Const("Какие избранные хотите просмотреть?"),
        # TODO: вывод названия канала/видеоролика в избранном, и добавить отступы
        Button(Const("Видео"), id="favorites_video", on_click=to_favorites_video),
        Button(Const("Каналы"), id="favorites_channel", on_click=to_favorites_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.favorites,
    ),
    Window(
        Format(
            "Список 10 последних избранных видео:\n{text1}"),
        Button(Const("Просмотреть всё"), id="view_all_favorites_video", on_click=to_view_all_favorites_video),
        Button(Const("Добавить видео в избранное по ссылке"), id="add_video_in_favorites",
               on_click=to_add_video_in_favorites),
        Button(Const("Удалить видео из избранного по ссылке"), id="delete_video_in_favorites",
               on_click=to_delete_video_in_favorites),
        Button(Const("Назад"), id="back_in_favorites", on_click=to_favorites),
        getter=get_data_last_ten_favorites_video,
        state=DialogUser.favorites_video,
    ),
    Window(
        Format("Список избранных видео:\n{text3}"),
        Button(Const("Назад"), id="back_in_last_ten_favorites_video", on_click=to_back_in_last_ten_favorites_video),
        getter=get_data_favorites_video,
        state=DialogUser.view_all_video_in_favorites,
    ),
    Window(
        Const("Введите URL видео которое хотите добавить."),
        Button(Const("Отмена"), id="back_in_last_ten_favorites_video", on_click=to_back_in_last_ten_favorites_video),
        MessageInput(input_url_video_to_add_in_favorites),
        state=DialogUser.add_video_in_favorites,
    ),
    Window(
        Const("Введите URL видео которое хотите удалить."),
        Button(Const("Отмена"), id="back_in_last_ten_favorites_video", on_click=to_back_in_last_ten_favorites_video),
        MessageInput(input_url_video_to_delete_in_favorites),
        state=DialogUser.delete_video_in_favorites,
    ),
    Window(
        Format("Список 10 последних избранных каналов:\n{text2}"),
        Button(Const("Просмотреть всё"), id="view_all_favorites_channel", on_click=to_view_all_favorites_channel),
        Button(Const("Добавить каналов в избранное по ссылке"), id="add_channel_in_favorites",
               on_click=to_add_channel_in_favorites),
        Button(Const("Удалить канал из избранного по ссылке"), id="delete_channel_in_favorites",
               on_click=to_delete_channel_in_favorites),
        Button(Const("Назад"), id="back_in_favorites", on_click=to_favorites),
        getter=get_data_last_ten_favorites_channel,
        state=DialogUser.favorites_channel,
    ),
    Window(
        Format("Список избранных каналов:\n{text4}"),
        Button(Const("Назад"), id="back_in_last_ten_favorites_channel", on_click=to_back_in_last_ten_favorites_channel),
        getter=get_data_favorites_channel,
        state=DialogUser.view_all_channel_in_favorites,
    ),
    Window(
        Const("Введите URL канала которое хотите добавить."),
        Button(Const("Отмена"), id="back_in_last_ten_favorites_channel",
               on_click=to_back_in_last_ten_favorites_channel),
        MessageInput(input_url_channel_to_add_in_favorites),
        state=DialogUser.add_channel_in_favorites,
    ),
    Window(
        Const("Введите URL канала которое хотите удалить."),
        Button(Const("Отмена"), id="back_in_last_ten_favorites_channel",
               on_click=to_back_in_last_ten_favorites_channel),
        MessageInput(input_url_channel_to_delete_in_favorites),
        state=DialogUser.delete_channel_in_favorites,
    ),
    Window(
        Const("Какую историю хотите просмотреть?"),
        # TODO: вывод названия канала/видеоролика в избранном
        Button(Const("Видео"), id="history_video", on_click=to_history_video),
        Button(Const("Каналы"), id="history_channel", on_click=to_history_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.history,
    ),
    Window(
        Format("Список 10 последних видео в истории:\n{text5}"),
        Button(Const("Просмотреть всё"), id="view_all_history_video", on_click=to_view_all_history_video),
        Button(Const("Назад"), id="history", on_click=to_history),
        getter=get_data_last_ten_history_video,
        state=DialogUser.history_video,
    ),
    Window(
        Format("Список истории видео:\n{text7}"),
        Button(Const("Назад"), id="history_video", on_click=to_history_video),
        getter=get_data_history_video,
        state=DialogUser.view_all_video_in_history,
    ),
    Window(
        Format("Список 10 последних каналов в истории:\n{text6}"),
        Button(Const("Просмотреть всё"), id="view_all_history_channel", on_click=to_view_all_history_channel),
        Button(Const("Назад"), id="history", on_click=to_history),
        getter=get_data_history_channel,
        state=DialogUser.history_channel,
    ),
    Window(
        Format("Список истории каналов:\n{text8}"),
        Button(Const("Назад"), id="history_channel", on_click=to_history_channel),
        getter=get_data_last_ten_history_channel,
        state=DialogUser.view_all_channel_in_history,
    ),
    Window(
        Const("Данный бот может:"
              "\n1. ----------"
              "\n2. ----------"
              "\n3. ----------"
              "\nКоманды для бота:"
              "\n/start - запуск бота"
              "\nКоманды для быстрого перемещения:"
              "\n/home page - домашняя страница (главная)"
              "\n/analysis - анализ"
              "\n/favorites - избранные URL"
              "\n/history - история запросов"),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.help,
    ),
    # Window(
    #     # TODO: сделать отображение настроек
    #     Const("Тут будет просмотр глобальных настроек"),
    #     Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
    #     state=DialogUser.settings,
    # ),
    Window(
        Const("Вы уверены что хотите выйти?"),
        Button(Const("Да"), id="yes", on_click=to_yes),
        Button(Const("Нет"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.exit,
    )
)

# async def settings(m: Message, dialog_manager: DialogManager):
#     # it is important to reset stack because user wants to restart everything
#     await dialog_manager.switch_to(DialogUser.settings)
