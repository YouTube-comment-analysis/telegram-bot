import operator
import threading
from datetime import date, datetime
from threading import Thread

from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Calendar, Radio
from aiogram_dialog.widgets.text import Const, Format, Multi, Progress
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, BaseDialogManager
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.when import Whenable
from typing import Dict
import authorization
import check_input_data
import search
from authorization_process.auth import get_authed_user_id, change_password
from authorization_process.password_encryption import is_correct_password
from comment_scrapping.comment import Comment
from database_interaction.auth import get_password, get_user_login
from database_interaction.global_settings import Settings
from database_interaction.promocode import use_promocode
from database_interaction.user import get_user_cabinet, get_user_role, UserRole

import database

from interface.FSM import DialogSign, DialogUser, DialogAdmin, DialogMngr
from search import get_video_comments_count, is_channel_url_correct, is_video_url_correct

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


"""Проанализировать"""


async def to_analysis(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis)


async def to_analysis_param(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_param)


# is_stop_download_comments = False


# async def to_cancel_downoload(c: CallbackQuery, button: Button, manager: DialogManager):
#     global is_stop_download_comments
#     is_stop_download_comments = True
#     # TODO: тут он должен после смены флага стопорнуться
#     await manager.dialog().switch_to(DialogUser.analysis)


popular_or_no = None  # 1 - по популярности, '2' - по времени
investment_or_not = None  # 1 - учитывать вложение, 2 - не учитывать вложение

import array_storage
from database_interaction.video import ScrapBy
import asyncio


# async def to_download(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.downoland_comments)
#     """Для загрузки кросбара"""
#     asyncio.create_task(background(c, manager.bg()))


async def to_back_in_param(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_param)


async def to_analysis_db(c: CallbackQuery, button: Button, manager: DialogManager):
    global popular_or_no
    global investment_or_not
    popular_or_no = manager.dialog().find("r_popular_or_date").get_checked()
    investment_or_not = manager.dialog().find("r_investment_or_not").get_checked()

    data = await get_data_db_downolader(manager)
    if data['have_db']:
        if popular_or_no is not None and investment_or_not is not None:
            await manager.dialog().switch_to(DialogUser.analysis_db)
        else:
            manager.answer(f"Вы не выбрали параметры.")
            await manager.dialog().switch_to(DialogUser.analysis_param)
    else:
        await manager.dialog().switch_to(DialogUser.downoland_comments)
        """Для загрузки кросбара"""
        asyncio.create_task(background(c, manager.bg()))


async def to_not_pump_up(c: CallbackQuery, button: Button, manager: DialogManager):
    order_by_date = False if popular_or_no == 1 else True
    arr = database.comment.extract_comments(
        input_url.split('https://www.youtube.com/watch?v=')[1], order_by_date)
    # TODO: Максим доделай
    # array_storage.add_arr_to_storage(manager.event.from_user.id, arr)
    await manager.dialog().switch_to(DialogUser.choose_analysis)


async def to_download(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.downoland_comments)
    """Для загрузки кросбара"""
    asyncio.create_task(background(c, manager.bg()))


input_url: str = None


async def background(c: CallbackQuery, manager: BaseDialogManager):
    global input_url
    url = input_url.split('https://www.youtube.com/watch?v=')[1]
    channel_id = search.get_chanel_url_by_video(input_url).split('https://www.youtube.com/')[1]
    in_popular_order = True if popular_or_no == 1 else False
    comments = []
    max_comment = database.global_settings.get_global_setting(Settings.max_comments)
    if investment_or_not == '1':
        total_count = search.get_video_comments_count(input_url)
    else:
        total_count = round(search.get_video_comments_count(input_url) * 0.66)
    count_downloader = 0
    if total_count > max_comment:
        total_count = max_comment
    for comment in search.get_comments_from_video(input_url, is_sort_by_recent_needed=not in_popular_order):
        # if is_stop_download_comments:
        #     await manager.switch_to(DialogUser.analysis)
        #     # await dialog_manager.dialog().switch_to(DialogUser.analysis)
        #     return
        # el
        if count_downloader > max_comment:
            break
        else:
            count_downloader += 1
            if count_downloader % (round(total_count / 10)) == 0:
                await asyncio.sleep(1)
                await manager.update({"progress": count_downloader * 100 / total_count, })
            comments.append(comment)
    await asyncio.sleep(0.5)
    await manager.switch_to(DialogUser.choose_analysis)

    # await manager.done()

    def load_to_db_thread(video_id: str, channel_id: str, comment: [Comment], in_popular: bool):
        database.comment.reload_comments(video_id, channel_id, comment, in_popular)

    threading.Thread(target=load_to_db_thread, args=(url, channel_id, comments, in_popular_order)).start()


async def get_data_max_count_comments(dialog_manager: DialogManager, **kwargs):
    max_com = database.global_settings.get_global_setting(Settings.max_comments)
    # dialog_data = dialog_manager.current_context().dialog_data
    return {
        "max_count_comments": max_com,
    }


async def to_add_photo_png(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(DialogUser.add_photo_png)


async def to_choose_analysis(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(DialogUser.choose_analysis)


async def to_analysis_video(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_video)


async def to_analysis_channel(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_channel)


async def get_data(**kwargs):
    count_com = get_video_comments_count(input_url)
    investment_or_not = [
        ("Учитывать вложенные", '1'),
        ("Не учитывать вложенные", '2'),
        # ("Orange", '3'),
        # ("Banana", '4'),
    ]
    popular_or_date = [
        ("По популярности", '1'),
        ("По дате", '2'),
        # ("Orange", '3'),
        # ("Banana", '4'),
    ]
    return {
        "count_com": count_com,
        "investment_or_not": investment_or_not,
        "popular_or_date": popular_or_date,
        "count": len(popular_or_date),
    }


async def get_data_db_downolader(dialog_manager: DialogManager, **kwargs):
    video_id = input_url.split("https://www.youtube.com/watch?v=")[1]
    scrap = database.video.ScrapBy
    scrap_by: str
    if popular_or_no == '1':
        scrap_by = scrap.popular
    else:
        scrap_by = scrap.date
    have = database.video.have_video_comments(video_id, scrap_by)
    last_date = database.video.get_scrap_date(video_id, scrap_by) if have else None
    return {
        "have_db": have,
        "date": last_date
    }


count_downloader = 0
total_count = 0
download_done = False


async def get_data_count_downolader(dialog_manager: DialogManager, **kwargs):
    # await manager.dialog().switch_to(DialogUser.downoland_comments)
    return {
        "progress": dialog_manager.current_context().dialog_data.get("progress", 0)
    }


async def input_url_video_to_analysis(m: Message, dialog: ManagedDialogAdapterProto,
                                      manager: DialogManager):
    # TODO: MAXIM/ILIYA получение url видео для анализа, сделать проверку на то видео ли это
    global input_url
    input_url = m.text
    await manager.dialog().switch_to(DialogUser.analysis_param)


async def input_url_channel_to_analysis(m: Message, dialog: ManagedDialogAdapterProto,
                                        manager: DialogManager):
    # TODO: MAXIM/ILIYA получение url канала для анализа, сделать проверку на то канала ли это
    global input_url
    input_url = m.text
    await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)


async def to_analysis_first_date_selected(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)


analysis_first_date_selected = None
analysis_second_date_selected = None


async def on_analysis_first_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    global analysis_first_date_selected
    analysis_first_date_selected = selected_date
    await manager.dialog().switch_to(DialogUser.analysis_second_date_selected)
    # await c.answer(str(selected_date))


async def on_analysis_second_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    if check_input_data.CheckInputData.date_lesser_check(analysis_first_date_selected, selected_date):
        global analysis_second_date_selected
        analysis_second_date_selected = selected_date
        await manager.dialog().switch_to(DialogUser.analysis_param)
    else:
        await manager.answer(f"Неверные даты.")
        await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)


async def to_analysis_world_cloud(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogUser.analysis_world_cloud)


async def input_photo_png(m: Message, dialog: ManagedDialogAdapterProto,
                                        manager: DialogManager):
    input_url = m.text
    await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)



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
    if is_video_url_correct(url):
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
    if is_video_url_correct(url):
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
    if is_channel_url_correct(url):
        id = url.split('www.youtube.com/')[1]
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
    if is_channel_url_correct(url):
        id = url.split('www.youtube.com/')[1]
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
    # TODO: сделать как то ссылку адекватную
    return {
        "text8": "У вас нет каналов в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
                    Ссылка на канал: https://www.youtube.com/{x.channel_id}
                    Дата анализа: {x.viewing_date}
                """, history))),
    }


"""Помощь"""

# async def to_help(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.help)


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
        Button(Const("Проанализировать"), id="analysis", on_click=to_analysis),
        Button(Const("Избранное"), id="favorites", on_click=to_favorites),
        # Button(Const("Помощь"), id="help", on_click=to_help),
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
        Format(
            "Что хотите проанализировать?\nЗАМЕЧАНИЕ: Анализ будет произведен максимум для {max_count_comments} комментариев"),
        Button(Const("Видео"), id="analysis_video", on_click=to_analysis_video),
        Button(Const("Канал"), id="analysis_channel", on_click=to_analysis_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.analysis,
        getter=get_data_max_count_comments,
    ),
    Window(
        Const("Введите URL видео"),
        Button(Const("Отмена"), id="analysis", on_click=to_analysis),
        MessageInput(input_url_video_to_analysis),
        state=DialogUser.analysis_video,
    ),
    Window(
        Const("Введите URL канала"),
        Button(Const("Отмена"), id="analysis", on_click=to_analysis),
        MessageInput(input_url_channel_to_analysis),
        state=DialogUser.analysis_channel,
    ),
    Window(
        Calendar(id='first_date_selected_calendar', on_click=on_analysis_first_date_selected),
        Const("Введите дату начала анализа"),
        Button(Const("Назад"), id="analysis", on_click=to_analysis),
        # MessageInput(),
        state=DialogUser.analysis_first_date_selected,
    ),
    Window(
        Calendar(id='analysis_second_date_selected', on_click=on_analysis_second_date_selected),
        Const("Введите конечную дату анализа"),
        Button(Const("Назад"), id="analysis_first_date_selected", on_click=to_analysis_first_date_selected),
        state=DialogUser.analysis_second_date_selected,
    ),
    Window(
        Radio(
            Format("🔘 {item[0]}"),  # E.g `🔘 Apple`
            Format("⚪️ {item[0]}"),
            id="r_popular_or_date",
            item_id_getter=operator.itemgetter(1),
            items="popular_or_date",
        ),
        Radio(
            Format("🔘 {item[0]}"),  # E.g `🔘 Apple`
            Format("⚪️ {item[0]}"),
            id="r_investment_or_not",
            item_id_getter=operator.itemgetter(1),
            items="investment_or_not",
        ),
        Button(Const("Продолжить"), id="analysis_param", on_click=to_analysis_db),
        Button(Const("Назад"), id="analysis", on_click=to_analysis),
        Format("Примерное кол-во комментариев {count_com}, выберите фильтр:"
               "\n— по популярности или дате?"
               "\n— учитывать ли вложенные комментарии?"),
        getter=get_data,
        state=DialogUser.analysis_param,
    ),
    Window(
        Format("Данные в БД: {have_db}"
               "\nСамое позднее обновление - {date}"
               "\nНужно ли докачивать комментарии?"),
        Button(Const("Не нужно"), id="not_pump_up", on_click=to_not_pump_up),
        Button(Const("Нужно"), id="download", on_click=to_download),
        Button(Const("Назад"), id="analysis_param", on_click=to_analysis_param),
        getter=get_data_db_downolader,
        state=DialogUser.analysis_db,
    ),
    Window(
        Multi(
            Const("Выполняется загрузка комментариев, пожалуйста подождите..."),
            Progress("progress", 10),
        ),
        # Button(Const("Я работаю но это не точно..\nОтмена"), id="cancel_downoload", on_click=to_cancel_downoload),
        getter=get_data_count_downolader,
        state=DialogUser.downoland_comments,
    ),
    Window(
        Const("Скачано: {n} комментариев за {f} время.\nВыберите вид анализа"),
        Button(Const("Облако слов (WorldCloud)"), id="analysis_world_cloud", on_click=to_analysis_world_cloud),
        # Button(Const("Канал"), id="analysis_channel", on_click=to_analysis_channel),
        Button(Const("Назад к выбору параметров"), id="back_in_param", on_click=to_back_in_param),
        state=DialogUser.choose_analysis,
        # getter=get_data_max_count_comments,
    ),
    Window(
        Const(
            "Мы научились делать облако слов такой же формы, какой будет форма на фотографии, вам нужно ее отправить в .png."
            "\nХотите использовать данную функцию?"),
        Button(Const("Да"), id="add_photo_png", on_click=to_add_photo_png),
        # Button(Const("Нет"), id="result_world_cloud", on_click=to_result_world_cloud),
        Button(Const("Назад"), id="back_in_choose_analysis", on_click=to_choose_analysis),
        state=DialogUser.analysis_world_cloud,
    ),
    Window(
        Const(
            "Вставьте картинку, для лучшего результата нужно использовать светлую фотографию.\nНужный формат: .png"
            "\nХотите использовать данную функцию?"),
        # TODO: Доделать метод с получением фото от пользователя
        # type=ContentType.PHOTO,
        MessageInput(input_photo_png),
        # Button(Const("Отмена"), id="back_in_choose_analysis", on_click=to_choose_analysis),
        state=DialogUser.add_photo_png,
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
              "\n/start - запуск/перезапуск бота"
              "\nБыстрые перемещения:"
              "\n/home page - домашняя страница (главная)"
              "\n/analysis - анализ"
              "\n/favorites - избранные"
              "\n/history - история запросов"),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.help,
    ),
    Window(
        Format("Глобальных настроек:"
               "\nМаксимальное количество комментариев для скачивания за раз - {max_count_comments}"),
        Button(Const("Назад"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.settings,
        getter=get_data_max_count_comments,
    ),
    Window(
        Const("Вы уверены что хотите выйти?"),
        Button(Const("Да"), id="yes", on_click=to_yes),
        Button(Const("Нет"), id="back_in_home_page", on_click=to_back_in_home_page),
        state=DialogUser.exit,
    )
)


async def settings(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.settings)  # это костыль, разработчик библиотеки предложил его
    # await dialog_manager.switch_to(DialogUser.settings)


async def helps(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.help)  # это костыль, разработчик библиотеки предложил его


async def home_page(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.home_page)  # это костыль, разработчик библиотеки предложил его


async def analysis(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.analysis)  # это костыль, разработчик библиотеки предложил его


async def history(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.history)  # это костыль, разработчик библиотеки предложил его
