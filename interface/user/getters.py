import datetime

from aiogram_dialog import DialogManager

from analysis import phrases_pie_analysis, phrases_plot_analysis
from authorization_process import authorization
from database_interaction import database
from database_interaction.global_settings import Settings
from database_interaction.user import get_user_cabinet, get_user_role
from database_interaction.video import ScrapBy
from interface.FSM import DialogUser
from interface.user.auxiliary import reshow_message
from interface.user.user_variable_storage import add_variable_in_dict, get_variable_from_dict, UserVariable
from scraping import getting_information, getting_data
from authorization_process.auth import get_authed_user_id


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


async def get_data_max_count_comments(dialog_manager: DialogManager, **kwargs):
    max_com = database.global_settings.get_global_setting(Settings.max_comments)
    # dialog_data = dialog_manager.current_context().dialog_data
    return {
        "max_count_comments": max_com,
    }


async def get_data_radio_param_analysis(dialog_manager: DialogManager, **kwargs):
    first_button_state = dialog_manager.dialog().find("r_investment_or_not").get_checked()
    second_button_state = dialog_manager.dialog().find("r_popular_or_date").get_checked()

    if (first_button_state is None) and (second_button_state is None):
        url = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.input_url)
        if get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.is_url_video):
            mmm = getting_information.get_video_comments_amount(url)
            add_variable_in_dict(dialog_manager.event.from_user.id, UserVariable.list_of_videos, [url])
            add_variable_in_dict(dialog_manager.event.from_user.id, UserVariable.comment_total_count, mmm)
        else:
            start_date = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.analysis_first_date_selected)
            end_date = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.analysis_second_date_selected)
            await dialog_manager.event.bot.send_message(dialog_manager.event.from_user.id,
                                                        "Пожалуйста подождите.. я считаю сколько комментариев нужно посчитать.")
            videos_with_counts = getting_data.get_list_of_channel_videos_with_comment_count(url, start_date, end_date)
            # TODO тут бы прогресс бар прикрутить т.к. будет долго
            mmm = sum(pair['comment_count'] for pair in videos_with_counts)
            urls = []
            for pair in videos_with_counts:
                urls.append(pair['url'])
            add_variable_in_dict(dialog_manager.event.from_user.id, UserVariable.list_of_videos, urls)
            add_variable_in_dict(dialog_manager.event.from_user.id, UserVariable.comment_total_count, mmm)
    else:
        mmm = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.comment_total_count)

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
        "m": mmm,
        "investment_or_not": investment_or_not,
        "popular_or_date": popular_or_date,
    }


async def get_db(dialog_manager: DialogManager, **kwargs):
    videos_url = get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.list_of_videos)
    is_have_one = False
    min_date = datetime.datetime.now().date()
    for video_url in videos_url:
        video_id = video_url.split("https://www.youtube.com/watch?v=")[1]

        scrap_by: ScrapBy
        if get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.popular_or_no) == '1':
            scrap_by = ScrapBy.popular
        else:
            scrap_by = ScrapBy.date
        have = database.video.have_video_comments(video_id, scrap_by)
        is_have_one = is_have_one or have
        date = database.video.get_scrap_date(video_id, scrap_by)

        if date is not None:
            if date <= min_date:
                min_date = date
    return {
        "have_db": is_have_one,
        "date": min_date,
    }
    # return {"have_db": is_have_one, "date": min_date}


async def get_data_count_downolader(dialog_manager: DialogManager, **kwargs):
    return {
        "progress": dialog_manager.current_context().dialog_data.get("progress", 0)
    }


async def get_data_info_comments(dialog_manager: DialogManager, **kwargs):
    telegram_id = dialog_manager.event.from_user.id
    check, user_id = authorization.get_authed_user_id(telegram_id)
    video_url = get_variable_from_dict(telegram_id, UserVariable.input_url)
    if get_variable_from_dict(telegram_id, UserVariable.is_url_video):
        database.history.add_user_history_video(user_id, video_url.split('https://www.youtube.com/watch?v=')[1])
    else:
        channel_id = getting_information.get_chanel_url_by_video(video_url).split('https://www.youtube.com/')[1]
        database.channel.insert_channel(channel_id)
        database.history.add_user_channel_video(user_id, channel_id)
    time = get_variable_from_dict(dialog_manager.event.from_user.id,
                                                        UserVariable.download_time_sec)
    x = len(get_variable_from_dict(dialog_manager.event.from_user.id, UserVariable.comments_array))
    return {
        "time": time,
        "n": x,
    }


async def get_data_radio_sentiment_grouping(dialog_manager: DialogManager, **kwargs):
    phrases_chart1 = [
        ("По дням", '1'),
        ("По неделям", '2'),
        ("По месяцам", '3'),
        # ("Banana", '4'),
    ]
    return {
        "phrases_chart1": phrases_chart1,
    }


async def get_data_last_ten_history_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    history = database.history.get_user_channel_history(user_id, True)
    return {
        "text8": "У вас нет каналов в истории." if len(history) == 0 else
        "\n".join(list(map(lambda x: f"""
                    Ссылка на канал: https://www.youtube.com/{x.channel_id}
                    Дата анализа: {x.viewing_date}
                """, history))),
    }


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


async def get_data_favorites_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    data = database.favorite.get_favorite_user_channels(user_id, False)
    favorites_channel = list(map(lambda x: f"https://www.youtube.com/watch?v={x}",
                                 data))
    return {
        "text4": "У вас нет избранных каналов." if len(favorites_channel) == 0 else "\n".join(favorites_channel),
    }


async def get_data_favorites_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    data = database.favorite.get_favorite_user_videos(user_id, False)
    favorites_video = list(map(lambda x: f" https://www.youtube.com/watch?v={x}",
                               data))
    return {
        "text3": "У вас нет избранных видео." if len(favorites_video) == 0 else "\n".join(favorites_video),
    }


async def get_data_last_ten_favorites_channel(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    ten_favorites_channel = list(map(lambda x: f"https://www.youtube.com/c/{x}",
                                     database.favorite.get_favorite_user_channels(user_id, True)))
    return {
        "text2": "У вас нет избранных каналов." if len(ten_favorites_channel) == 0 else "\n".join(
            ten_favorites_channel),
    }


async def input_words_result2(dialog_manager: DialogManager, **kwargs):
    check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
    check_credits = database.user.get_user_credits(user_id) >= 1
    if check_credits:
        teleid = dialog_manager.event.from_user.id

        database.user.decrease_user_credits(user_id, 1)

        comments = get_variable_from_dict(teleid, UserVariable.comments_array)

        # TODO: замечание того, что фото должно обновляться в зависимости от даты (когда нажата кнопка "обновить")
        is_order_matter = get_variable_from_dict(teleid, UserVariable.is_order_matter)
        if get_variable_from_dict(teleid, UserVariable.is_in_loop):
            phrases = get_variable_from_dict(teleid, UserVariable.phrases)
            start_date = get_variable_from_dict(teleid, UserVariable.analysis_first_date_selected)
            end_date = get_variable_from_dict(teleid, UserVariable.analysis_second_date_selected)
        else:
            raise Exception
            #add_variable_in_dict(teleid, UserVariable.phrases, phrases)
            #start_date, end_date = None, None

        if get_variable_from_dict(teleid, UserVariable.is_chart_pie):
            image_path = phrases_pie_analysis.make_word_count_analysis_pie(comments, phrases, is_order_matter, start_date, end_date,
                                                             str(teleid))
        else:
            type_of_grouping = get_variable_from_dict(teleid, UserVariable.type_of_grouping)
            image_path = phrases_plot_analysis.make_word_count_analysis_plot(comments, phrases, type_of_grouping, is_order_matter,
                                                              start_date, end_date, str(teleid))

        photo = open(image_path, 'rb')
        await dialog_manager.event.bot.send_photo(dialog_manager.event.from_user.id, photo)
        photo.close()
        await reshow_message(dialog_manager)

        await dialog_manager.dialog().switch_to(DialogUser.analysis_result_input_words)
    else:
        await dialog_manager.event.reply("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
        await dialog_manager.dialog().switch_to(DialogUser.choose_analysis)


async def get_data_last_ten_favorites_video(dialog_manager: DialogManager, **kwargs):
    check, user_id = get_authed_user_id(dialog_manager.event.from_user.id)
    ten_favorites_video = list(map(lambda x: f" https://www.youtube.com/watch?v={x}",
                                   database.favorite.get_favorite_user_videos(user_id, True)))
    # # dialog_data = dialog_manager.current_context().dialog_data
    return {
        "text1": "У вас нет избранных видео." if len(ten_favorites_video) == 0 else "\n".join(ten_favorites_video),
    }


async def get_data_radio_phrases(dialog_manager: DialogManager, **kwargs):
    yes_or_no = [
        ("Да", '1'),
        ("Нет", '2'),
        # ("Orange", '3'),
        # ("Banana", '4'),
    ]
    phrases_chart = [
        ("По дням", '1'),
        ("По неделям", '2'),
        ("По месяцам", '3'),
        # ("Banana", '4'),
    ]
    return {
        "phrases_chart": phrases_chart,
        "yes_or_no": yes_or_no,
    }