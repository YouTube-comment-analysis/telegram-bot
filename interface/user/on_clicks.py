import asyncio
import datetime

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.manager.protocols import BaseDialogManager
from aiogram_dialog.widgets.kbd import Button

import check_input_data

from analysis import word_cloud, sentiment_analysis
from analysis.auxiliary import GroupingType
from authorization_process import authorization
from database_interaction import database
from database_interaction.global_settings import Settings
from database_interaction.video import ScrapBy
from interface.user import user_variable_storage, auxiliary
from interface.FSM import DialogUser, DialogSign
from interface.user.auxiliary import reshow_message
from interface.user.user_variable_storage import add_variable_in_dict, get_variable_from_dict, UserVariable, clear_user_variable_space
from scraping import getting_information, getting_data


async def to_home_page(c: CallbackQuery, button: Button, manager: DialogManager):
    clear_user_variable_space(c.from_user.id)
    await manager.switch_to(DialogUser.home_page)


async def on_analysis_first_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: datetime.date):
    add_variable_in_dict(manager.event.from_user.id, UserVariable.analysis_first_date_selected, selected_date)
    await manager.dialog().switch_to(DialogUser.analysis_second_date_selected)
    # await c.answer(str(selected_date))


async def back_to_analysis(c: CallbackQuery, button: Button, manager: DialogManager):
    del manager.current_context().widget_data["r_investment_or_not"]
    del manager.current_context().widget_data["r_popular_or_date"]
    await manager.dialog().switch_to(DialogUser.analysis)


async def on_analysis_second_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: datetime.date):
    teleid = manager.event.from_user.id
    if check_input_data.CheckInputData.date_lesser_check(
            get_variable_from_dict(teleid, UserVariable.analysis_first_date_selected),
            selected_date):
        add_variable_in_dict(teleid, UserVariable.analysis_second_date_selected, selected_date)
        add_variable_in_dict(teleid, UserVariable.is_in_loop, True)
        state = get_variable_from_dict(teleid, UserVariable.current_date_interval_state)
        if state == 0:
            await manager.dialog().switch_to(DialogUser.analysis_param)
        elif state == 1:
            await auxiliary.show_pie_or_graph(teleid, manager.event.message, manager)
            await manager.dialog().switch_to(DialogUser.analysis_result_input_words)
        elif state == 2:
            await show_sentiment_hist(teleid, manager)
            await manager.dialog().switch_to(DialogUser.analysis_sentiment_show_result)
        else:
            raise NotImplementedError
    else:
        await manager.event.reply(f"Неверные даты.")
        await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)


async def show_sentiment_hist(teleid: int, manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(teleid)
    check_credits = database.user.get_user_credits(user_id) >= 1
    if check_credits:
        database.user.decrease_user_credits(user_id, 1)

        comments = get_variable_from_dict(teleid, UserVariable.comments_array)
        type_of_grouping = get_variable_from_dict(teleid, UserVariable.type_of_grouping)
        if get_variable_from_dict(teleid, UserVariable.is_in_loop):
            start_date = get_variable_from_dict(teleid, UserVariable.analysis_first_date_selected)
            end_date = get_variable_from_dict(teleid, UserVariable.analysis_second_date_selected)
        else:
            start_date, end_date = None, None
        image_path = sentiment_analysis.make_sentiment_analysis_hist(comments, type_of_grouping, start_date, end_date,
                                                                     str(teleid))
        photo = open(image_path, 'rb')
        photo_manager = await manager.event.bot.send_photo(teleid, photo)
        photo.close()
        await reshow_message(manager)
    else:
        await manager.event.answer("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
        await manager.switch_to(DialogUser.choose_analysis)


async def to_analysis_db(c: CallbackQuery, button: Button, manager: DialogManager):
    popular_or_no = manager.dialog().find("r_popular_or_date").get_checked()
    investment_or_not = manager.dialog().find("r_investment_or_not").get_checked()

    add_variable_in_dict(manager.event.from_user.id, UserVariable.popular_or_no, popular_or_no)
    add_variable_in_dict(manager.event.from_user.id, UserVariable.investment_or_not, investment_or_not)
    # Вот щас прям вместо него, нужно прописать (а он у вас уже готовый где то использовался)
    # метод который проверяет есть ли видео в бд или нет
    videos =  get_variable_from_dict(c.from_user.id, UserVariable.list_of_videos)
    popular_or_no = get_variable_from_dict(c.from_user.id, UserVariable.popular_or_no)
    data = is_videos_in_bd(videos, popular_or_no)
    if data:
        if popular_or_no is not None and investment_or_not is not None:
            await manager.dialog().switch_to(DialogUser.analysis_db)
        else:
            await c.message.answer(f"Вы не выбрали параметры.")
            await manager.dialog().switch_to(DialogUser.analysis_param)
    else:
        add_variable_in_dict(manager.event.from_user.id, UserVariable.is_stop_download_comments, False)
        await manager.dialog().switch_to(DialogUser.downoland_comments)
        """Для загрузки кросбара"""
        asyncio.create_task(background(c, manager.bg()))


async def background(c: CallbackQuery, manager: BaseDialogManager):
    teleid = c.from_user.id

    first_video_url = get_variable_from_dict(teleid, UserVariable.list_of_videos)[0]
    channel_id = getting_information.get_chanel_url_by_video(first_video_url).split('https://www.youtube.com/')[1]
    in_popular_order = True if get_variable_from_dict(c.from_user.id, UserVariable.popular_or_no) == '1' else False

    max_comment = database.global_settings.get_global_setting(Settings.max_comments)

    if get_variable_from_dict(teleid, UserVariable.is_url_video):
        total_count = getting_information.get_video_comments_amount(first_video_url)
    else:
        total_count = get_variable_from_dict(teleid, UserVariable.comment_total_count)
    if get_variable_from_dict(c.from_user.id, UserVariable.investment_or_not) == '2':
        total_count = round(total_count * 0.66)

    if total_count > max_comment:
        total_count = max_comment

    start_time = datetime.datetime.now()

    count_downloader = 0
    comments = []
    for video_url in get_variable_from_dict(teleid, UserVariable.list_of_videos):
        comments_from_video = []
        for comment in getting_data.get_comments_from_video_iterator(video_url, is_sort_by_recent_needed=not in_popular_order):
            if get_variable_from_dict(c.from_user.id, UserVariable.is_stop_download_comments):
                await manager.switch_to(DialogUser.analysis)
                return
            elif count_downloader >= max_comment:
                break
            else:
                if count_downloader % (round(total_count / 10)) == 0:
                    await asyncio.sleep(1)
                    await manager.update({"progress": min(round(count_downloader / total_count * 10) * 10, 100), })
                comments.append(comment)
                comments_from_video.append(comment)
                count_downloader += 1
        database.comment.reload_comments(video_url.split('https://www.youtube.com/watch?v=')[1], channel_id, comments_from_video, in_popular_order)
        if count_downloader >= max_comment:
            break

    await asyncio.sleep(0.5)
    comment_total_count = len(comments)
    download_time_sec = (datetime.datetime.now() - start_time).seconds
    add_variable_in_dict(teleid, user_variable_storage.UserVariable.comment_total_count, comment_total_count)
    add_variable_in_dict(teleid, user_variable_storage.UserVariable.download_time_sec, download_time_sec)
    add_variable_in_dict(teleid, UserVariable.comments_array, comments)

    await manager.switch_to(DialogUser.choose_analysis)

    # def load_to_db_thread(video_id: str, channel_id: str, comment: [Comment], in_popular: bool):
    #     database.comment.reload_comments(video_id, channel_id, comment, in_popular)
    # threading.Thread(target=load_to_db_thread, args=(url, channel_id, comments, in_popular_order)).start()

    # await manager.done()


def is_videos_in_bd(videos_url: list, popular_or_no: str):
    for video_url in videos_url:
        video_id = video_url.split("https://www.youtube.com/watch?v=")[1]

        scrap_by: ScrapBy
        if popular_or_no == '1':
            scrap_by = ScrapBy.popular
        else:
            scrap_by = ScrapBy.date
        have = database.video.have_video_comments(video_id, scrap_by)
        if have:
            return True

    return False


async def to_result_world_cloud(m: CallbackQuery, button: Button, manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    check_credits = database.user.get_user_credits(user_id) >= 1
    if check_credits:
        database.user.decrease_user_credits(user_id, 1)

        await m.bot.send_message(m.message.chat.id, "Подождите пожалуйста... Мне нужно подумать")
        # await m.message.reply("Подождите пожалуйста... Мне нужно подумать")
        # await m.answer("Подождите пожалуйста... Мне нужно подумать")
        path = fr'photos\output_{m.from_user.id}.png'
        arr = user_variable_storage.get_variable_from_dict(m.from_user.id, UserVariable.comments_array)
        # arr = database.comment.extract_comments(
        #     get_variable_from_dict(manager.event.from_user.id, UserVariable.input_url).split(
        #         'https://www.youtube.com/watch?v=')[1], False)
        word_cloud.create_default_word_cloud(arr, path)
        photo = open(path, 'rb')
        await manager.event.bot.send_photo(m.message.chat.id, photo)
        await reshow_message(manager)
        # await m.bot.send_photo(m.message.chat.id, photo) # РАБОЧИЙ
        photo.close()
        await manager.dialog().switch_to(DialogUser.analysis_result_word_cloud)
        #await manager.switch_to(DialogUser.analysis_result_word_cloud)
    else:
        await m.answer("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
        await manager.dialog().switch_to(DialogUser.choose_analysis)


async def to_not_pump_up(c: CallbackQuery, button: Button, manager: DialogManager):
    order_by_date = False if get_variable_from_dict(manager.event.from_user.id,
                                                    UserVariable.popular_or_no) == '1' else True
    start_time = datetime.datetime.now()
    arr = database.comment.extract_comments(
        get_variable_from_dict(manager.event.from_user.id, UserVariable.input_url).split(
            'https://www.youtube.com/watch?v=')[1], order_by_date)
    add_variable_in_dict(manager.event.from_user.id, user_variable_storage.UserVariable.comments_array, arr)
    download_time_sec = (datetime.datetime.now() - start_time).seconds
    add_variable_in_dict(c.from_user.id, user_variable_storage.UserVariable.download_time_sec, download_time_sec)
    await manager.dialog().switch_to(DialogUser.choose_analysis)


async def to_download(c: CallbackQuery, button: Button, manager: DialogManager):
    add_variable_in_dict(manager.event.from_user.id, UserVariable.is_stop_download_comments, False)
    await manager.dialog().switch_to(DialogUser.downoland_comments)
    """Для загрузки кросбара"""
    asyncio.create_task(background(c, manager.bg()))


async def to_cancel_downoload(c: CallbackQuery, button: Button, manager: DialogManager):
    add_variable_in_dict(c.from_user.id, UserVariable.is_stop_download_comments, True)
    await manager.switch_to(DialogUser.analysis)


async def to_analysis_phrase_param(c: CallbackQuery, button: Button, manager: DialogManager):
    add_variable_in_dict(manager.event.from_user.id, UserVariable.current_date_interval_state, 1)
    yes = manager.dialog().find("r_yes_or_no").get_checked() # '1' да, '2' нет
    if yes == '1':
        add_variable_in_dict(c.from_user.id, UserVariable.is_order_matter, True)
    elif yes == '2':
        add_variable_in_dict(c.from_user.id, UserVariable.is_order_matter, False)
    else:
        await c.message.answer(f"Вы не выбрали данные.")
        await manager.dialog().switch_to(DialogUser.analysis_phrases)
        return
    grouping = manager.dialog().find("r_phrases_chart").get_checked()  # None => график, '1', '2', '3'
    if grouping == '1':
        add_variable_in_dict(manager.event.from_user.id, UserVariable.type_of_grouping, GroupingType.day)
    elif grouping == '2':
        add_variable_in_dict(manager.event.from_user.id, UserVariable.type_of_grouping, GroupingType.week)
    elif grouping == '3':
        add_variable_in_dict(manager.event.from_user.id, UserVariable.type_of_grouping, GroupingType.month)

    add_variable_in_dict(c.from_user.id, UserVariable.is_in_loop, False)

    await manager.switch_to(DialogUser.input_words)


async def to_analysis_sentiment(c: CallbackQuery, button: Button, manager: DialogManager):
    teleid = c.from_user.id
    add_variable_in_dict(teleid, UserVariable.current_date_interval_state, 2)

    grouping = manager.dialog().find("r_sentiment_chart1").get_checked()  # None => график, '1', '2', '3'
    if grouping == '1':
        add_variable_in_dict(teleid, UserVariable.type_of_grouping, GroupingType.day)
    elif grouping == '2':
        add_variable_in_dict(teleid, UserVariable.type_of_grouping, GroupingType.week)
    elif grouping == '3':
        add_variable_in_dict(teleid, UserVariable.type_of_grouping, GroupingType.month)
    else:
        await c.message.answer(f"Вы не выбрали данные.")
        await manager.dialog().switch_to(DialogUser.analysis_sentiment_param)
        return
    add_variable_in_dict(c.from_user.id, UserVariable.is_in_loop, False)

    await show_sentiment_hist(teleid, manager)

    await manager.dialog().switch_to(DialogUser.analysis_sentiment_show_result)


async def to_phrase_param_pie(c: CallbackQuery, button: Button, manager: DialogManager):
    add_variable_in_dict(c.from_user.id, UserVariable.is_chart_pie, True)
    await manager.dialog().switch_to(DialogUser.analysis_phrase_param)


async def to_phrase_param_graph(c: CallbackQuery, button: Button, manager: DialogManager):
    add_variable_in_dict(c.from_user.id, UserVariable.is_chart_pie, False)
    await manager.dialog().switch_to(DialogUser.analysis_phrase_param)


async def to_yes(c: CallbackQuery, button: Button, manager: DialogManager):
    user_variable_storage.delete_user_variables(manager.event.from_user.id)
    authorization.sign_out(manager.event.from_user.id)
    await manager.start(DialogSign.start)