import operator

from aiogram.types import ContentType
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Radio, SwitchTo, Calendar
from aiogram_dialog.widgets.text import Const, Format, Progress, Multi

from interface.FSM import DialogUser, DialogAdmin, DialogMngr
from interface.user import on_clicks, getters, conditions, inputs

dialog_user = Dialog(
    Window(
        Const("Добро пожаловать на главую страницу!"),
        SwitchTo(Const("АдминМод"), id="admin", when=conditions.is_admin, state=DialogAdmin.start),
        SwitchTo(Const("МенеджерМод"), id="manager", when=conditions.is_manager, state=DialogMngr.start),
        SwitchTo(Const("Личный кабинет"), id="personal_area", state=DialogUser.personal_area),
        SwitchTo(Const("Проанализировать"), id="analysis", state=DialogUser.analysis),
        SwitchTo(Const("Избранное"), id="favorites", state=DialogUser.favorites),
        # Button(Const("Помощь"), id="help", on_click=to_help),
        SwitchTo(Const("История"), id="history", state=DialogUser.history),
        SwitchTo(Const("Выход"), id="exit", state=DialogUser.exit),
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
        SwitchTo(Const("Активировать промокод"), id="activate_promo", state=DialogAdmin.role_changer),
        SwitchTo(Const("Изменить пароль"), id="change_passw", state=DialogUser.input_old_passw),
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.personal_area,
        getter=getters.get_data_personal_area,
    ),
    Window(
        Const("Введите номер промокода."),
        SwitchTo(Const("Отмена"), id="cancel", state=DialogUser.personal_area),
        MessageInput(inputs.promo_handler),
        state=DialogUser.activate_promo,
    ),
    Window(
        Const("Для того, чтобы изменить пароль, введите старый пароль."),
        SwitchTo(Const("Отмена"), id="cancel", state=DialogUser.personal_area),
        MessageInput(inputs.input_old_passw_handler),
        state=DialogUser.input_old_passw,
    ),
    Window(
        Const("Теперь введите ваш новый пароль."),
        SwitchTo(Const("Отмена"), id="cancel", state=DialogUser.personal_area),
        MessageInput(inputs.input_new_passw_handler),
        state=DialogUser.input_new_passw,
    ),
    Window(
        Format(
            "Что хотите проанализировать?\nЗАМЕЧАНИЕ: Анализ будет произведен максимум для {max_count_comments} комментариев"),
        SwitchTo(Const("Видео"), id="analysis_video", state=DialogUser.analysis_video),
        SwitchTo(Const("Канал"), id="analysis_channel", state=DialogUser.analysis_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.analysis,
        getter=getters.get_data_max_count_comments,
    ),
    Window(
        Const("Введите URL видео"),
        SwitchTo(Const("Отмена"), id="to_analysis", state=DialogUser.analysis),
        MessageInput(inputs.input_url_video_to_analysis),
        state=DialogUser.analysis_video,
    ),
    Window(
        Const("Введите URL канала"),
        SwitchTo(Const("Отмена"), id="to_analysis", state=DialogUser.analysis),
        MessageInput(inputs.input_url_channel_to_analysis),
        state=DialogUser.analysis_channel,
    ),
    Window(
        Calendar(id='first_date_selected_calendar', on_click=on_clicks.on_analysis_first_date_selected),
        Const("Введите дату начала анализа"),
        Button(Const("Назад"), id="back_to_analysis", on_click=on_clicks.back_to_analysis),
        # MessageInput(),
        state=DialogUser.analysis_first_date_selected,
    ),
    Window(
        Calendar(id='analysis_second_date_selected', on_click=on_clicks.on_analysis_second_date_selected),
        Const("Введите конечную дату анализа"),
        SwitchTo(Const("Назад"), id="analysis_first_date_selected", state=DialogUser.analysis_first_date_selected),
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
        Button(Const("Продолжить"), id="analysis_param", on_click=on_clicks.to_analysis_db),
        Button(Const("Назад"), id="back_to_analysis", on_click=on_clicks.back_to_analysis),
        Format("Примерное количество комментариев: {m}\nВыберите фильтр:"
               "\n— по популярности или дате?"
               "\n— учитывать ли вложенные комментарии?"),
        getter=getters.get_data_radio_param_analysis,
        state=DialogUser.analysis_param,
    ),
    Window(
        Format("Данные в БД: {have_db}"
               "\nСамое позднее обновление {date}"
               "\nНужно ли докачивать комментарии?"),
        Button(Const("Не нужно"), id="not_pump_up", on_click=on_clicks.to_not_pump_up),
        Button(Const("Нужно"), id="download", on_click=on_clicks.to_download),
        SwitchTo(Const("Назад"), id="analysis_param", state=DialogUser.analysis_param),
        getter=getters.get_db,
        state=DialogUser.analysis_db,
    ),
    Window(
        Multi(
            Const("Выполняется загрузка комментариев, пожалуйста подождите..."),
            Progress("progress", 10),
        ),
        Button(Const("Отмена"), id="cancel_downoload", on_click=on_clicks.to_cancel_downoload),
        getter=getters.get_data_count_downolader,
        state=DialogUser.downoland_comments,
    ),
    Window(
        Format("Найдено {n} комментариев за {time} секунд.\nВыберите вид анализа"),
        SwitchTo(Const("Облако слов (WorldCloud)"), id="analysis_world_cloud", state=DialogUser.analysis_world_cloud),
        SwitchTo(Const("Кол-во слов/словосочетаний"), id="analysis_phrases", state=DialogUser.analysis_phrases),
        SwitchTo(Const("Сентимент анализ"), id="analysis_sentiment", state=DialogUser.analysis_sentiment_param),
        SwitchTo(Const("Назад к выбору параметров"), id="back_in_param", state=DialogUser.analysis_param),
        state=DialogUser.choose_analysis,
        getter=getters.get_data_info_comments,
    ),
    Window(
        Const("Выберите фильтр:\n- важен ли порядок слов?"),
        Radio(
            Format("🔘 {item[0]}"),  # E.g `🔘 Да `
            Format("⚪️ {item[0]}"),
            id="r_yes_or_no",
            item_id_getter=operator.itemgetter(1),
            items="yes_or_no",
        ),
        Const("какая группировка должна быть?", when=conditions.is_graph),
        Radio(
            Format("🔘 {item[0]}"),  # E.g `🔘 По дням`
            Format("⚪️ {item[0]}"),
            id="r_phrases_chart",
            when=conditions.is_graph,
            item_id_getter=operator.itemgetter(1),
            items="phrases_chart",
        ),
        Button(Const("Продолжить"), id="analysis_phrase_param", on_click=on_clicks.to_analysis_phrase_param),
        SwitchTo(Const("Назад"), id="back_in_analysis_phrases", state=DialogUser.analysis_phrases),
        state=DialogUser.analysis_phrase_param,
        getter=getters.get_data_radio_phrases,
    ),
    Window(
        Const("Какая группировка должна быть?"), #сентимент анализ
        Radio(
            Format("🔘 {item[0]}"),  # E.g `🔘 По дням`
            Format("⚪️ {item[0]}"),
            id="r_sentiment_chart1",
            item_id_getter=operator.itemgetter(1),
            items="phrases_chart1",
        ),
        Button(Const("Продолжить"), id="analysis_sentiment_param", on_click=on_clicks.to_analysis_sentiment),
        SwitchTo(Const("Назад"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_sentiment_param,
        getter=getters.get_data_radio_sentiment_grouping,
    ),
    Window(
        Const("Анализ фраз.\nВыберите вид представления данных"),
        Button(Const("Круговая диаграмма"), id="phrase_param_chart", on_click=on_clicks.to_phrase_param_pie),
        Button(Const("График"), id="phrase_param_graph", on_click=on_clicks.to_phrase_param_graph),
        SwitchTo(Const("Назад"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_phrases,
    ),
    Window(
        Const("Введите фразы (слово или несколько слов через пробел), разделяя фразы запятыми."),
        SwitchTo(Const("Отмена"), id="back_to_analysis_phrases", state=DialogUser.analysis_phrases),
        MessageInput(inputs.input_words_result),
        state=DialogUser.input_words,
    ),
    Window(
        Const("Введите фразы (слово или несколько слов через пробел), разделяя фразы запятыми."),
        SwitchTo(Const("Отмена"), id="back_to_analysis_phrases", state=DialogUser.analysis_phrases),
        getter=getters.input_words_result2,
        state=DialogUser.words_without_inmut,
    ),
    Window(
        # StaticMedia(path=r"D:\PycharmProjects\telegram-bot\word_cloud_data\test-wordcloud-from-mess.png",
        #             type=ContentType.PHOTO),
        Const("Ваш результат с словосочетаниями/словами готов!"),
        SwitchTo(Const("Обновить по новому выбранному интервалу"), id="analysis_first_date_selected", state=DialogUser.analysis_first_date_selected),
        SwitchTo(Const("Назад к анализу"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_result_input_words,
    ),
    Window(
        Const("Ваш результат с сентимент анализом готов!!"),
        SwitchTo(Const("Обновить по новому выбранному интервалу"), id="analysis_first_date_selected", state=DialogUser.analysis_first_date_selected),
        SwitchTo(Const("Назад к анализу"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        # StaticMedia(
        #         path=get_path_to_photo,
        #         type=ContentType.PHOTO
        #     ),
        state=DialogUser.analysis_sentiment_show_result,
    ),
    Window(
        Const("Ваш результат с сентимент анализом готов!!"),
        SwitchTo(Const("Обновить по новому выбранному интервалу"), id="analysis_first_date_selected", state=DialogUser.analysis_first_date_selected),
        SwitchTo(Const("Назад к анализу"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_sentiment_result,
    ),
    Window(
        Const(
            "Мы научились делать облако слов такой же формы, какой будет форма на фотографии, вам нужно ее отправить в .png."
            "\nХотите использовать данную функцию?"),
        SwitchTo(Const("Да"), id="add_photo_png", state=DialogUser.add_photo_png),
        Button(Const("Нет"), id="result_world_cloud", on_click=on_clicks.to_result_world_cloud),
        SwitchTo(Const("Назад"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_world_cloud,
    ),
    Window(
        Const(
            "Вставьте картинку, для лучшего результата нужно использовать светлую фотографию."
            "\nХотите использовать данную функцию?"),
        MessageInput(inputs.input_photo_png, ContentType.PHOTO),
        SwitchTo(Const("Отмена"), id="back_to_analysis_world_cloud", state=DialogUser.analysis_world_cloud),
        state=DialogUser.add_photo_png,
    ),
    Window(
        # StaticMedia(path=r"D:\PycharmProjects\telegram-bot\word_cloud_data\test-wordcloud-from-mess.png",
        #             type=ContentType.PHOTO),
        Const("Ваш результат c облаком слов готов!"),
        SwitchTo(Const("Назад к анализу"), id="back_in_choose_analysis", state=DialogUser.choose_analysis),
        state=DialogUser.analysis_result_word_cloud,
    ),
    Window(
        Const("Какие избранные хотите просмотреть?"),
        # TODO: вывод названия канала/видеоролика в избранном, и добавить отступы
        SwitchTo(Const("Видео"), id="favorites_video", state=DialogUser.favorites_video),
        SwitchTo(Const("Каналы"), id="favorites_channel", state=DialogUser.favorites_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.favorites,
    ),
    Window(
        Format(
            "Список 10 последних избранных видео:\n{text1}"),
        SwitchTo(Const("Просмотреть всё"), id="view_all_favorites_video", state=DialogUser.view_all_video_in_favorites),
        SwitchTo(Const("Добавить видео в избранное по ссылке"), id="add_video_in_favorites",
               state=DialogUser.add_video_in_favorites),
        SwitchTo(Const("Удалить видео из избранного по ссылке"), id="delete_video_in_favorites",
               state=DialogUser.delete_video_in_favorites),
        SwitchTo(Const("Назад"), id="back_in_favorites", state=DialogUser.favorites),
        getter=getters.get_data_last_ten_favorites_video,
        state=DialogUser.favorites_video,
    ),
    Window(
        Format("Список избранных видео:\n{text3}"),
        SwitchTo(Const("Назад"), id="back_in_last_ten_favorites_video", state=DialogUser.favorites_video),
        getter=getters.get_data_favorites_video,
        state=DialogUser.view_all_video_in_favorites,
    ),
    Window(
        Const("Введите URL видео которое хотите добавить."),
        SwitchTo(Const("Отмена"), id="back_in_last_ten_favorites_video", state=DialogUser.favorites_video),
        MessageInput(inputs.input_url_video_to_add_in_favorites),
        state=DialogUser.add_video_in_favorites,
    ),
    Window(
        Const("Введите URL видео которое хотите удалить."),
        SwitchTo(Const("Отмена"), id="back_in_last_ten_favorites_video", state=DialogUser.favorites_video),
        MessageInput(inputs.input_url_video_to_delete_in_favorites),
        state=DialogUser.delete_video_in_favorites,
    ),
    Window(
        Format("Список 10 последних избранных каналов:\n{text2}"),
        SwitchTo(Const("Просмотреть всё"), id="view_all_favorites_channel", state=DialogUser.view_all_channel_in_favorites),
        SwitchTo(Const("Добавить каналов в избранное по ссылке"), id="add_channel_in_favorites",
               state=DialogUser.add_channel_in_favorites),
        SwitchTo(Const("Удалить канал из избранного по ссылке"), id="delete_channel_in_favorites",
               state=DialogUser.delete_channel_in_favorites),
        SwitchTo(Const("Назад"), id="back_in_favorites", state=DialogUser.favorites),
        getter=getters.get_data_last_ten_favorites_channel,
        state=DialogUser.favorites_channel,
    ),
    Window(
        Format("Список избранных каналов:\n{text4}"),
        SwitchTo(Const("Назад"), id="back_in_last_ten_favorites_channel", state=DialogUser.favorites_channel),
        getter=getters.get_data_favorites_channel,
        state=DialogUser.view_all_channel_in_favorites,
    ),
    Window(
        Const("Введите URL канала которое хотите добавить."),
        SwitchTo(Const("Отмена"), id="back_in_last_ten_favorites_channel",
               state=DialogUser.favorites_channel),
        MessageInput(inputs.input_url_channel_to_add_in_favorites),
        state=DialogUser.add_channel_in_favorites,
    ),
    Window(
        Const("Введите URL канала которое хотите удалить."),
        SwitchTo(Const("Отмена"), id="back_in_last_ten_favorites_channel",
               state=DialogUser.favorites_channel),
        MessageInput(inputs.input_url_channel_to_delete_in_favorites),
        state=DialogUser.delete_channel_in_favorites,
    ),
    Window(
        Const("Какую историю хотите просмотреть?"),
        # TODO: вывод названия канала/видеоролика в избранном
        SwitchTo(Const("Видео"), id="history_video", state=DialogUser.history_video),
        SwitchTo(Const("Каналы"), id="history_channel", state=DialogUser.history_channel),
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.history,
    ),
    Window(
        Format("Список 10 последних видео в истории:\n{text5}"),
        SwitchTo(Const("Просмотреть всё"), id="view_all_history_video", state=DialogUser.view_all_video_in_history),
        SwitchTo(Const("Назад"), id="history", state=DialogUser.history),
        getter=getters.get_data_last_ten_history_video,
        state=DialogUser.history_video,
    ),
    Window(
        Format("Список истории видео:\n{text7}"),
        SwitchTo(Const("Назад"), id="history_video", state=DialogUser.history_video),
        getter=getters.get_data_history_video,
        state=DialogUser.view_all_video_in_history,
    ),
    Window(
        Format("Список 10 последних каналов в истории:\n{text6}"),
        SwitchTo(Const("Просмотреть всё"), id="view_all_history_channel", state=DialogUser.view_all_channel_in_history),
        SwitchTo(Const("Назад"), id="history", state=DialogUser.history),
        getter=getters.get_data_history_channel,
        state=DialogUser.history_channel,
    ),
    Window(
        Format("Список истории каналов:\n{text8}"),
        SwitchTo(Const("Назад"), id="history_channel", state=DialogUser.history_channel),
        getter=getters.get_data_last_ten_history_channel,
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
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.help,
    ),
    Window(
        Format("Глобальных настроек:"
               "\nМаксимальное количество комментариев для скачивания за раз - {max_count_comments}"),
        Button(Const("Назад"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.settings,
        getter=getters.get_data_max_count_comments,
    ),
    Window(
        Const("Вы уверены что хотите выйти?"),
        Button(Const("Да"), id="yes", on_click=on_clicks.to_yes),
        Button(Const("Нет"), id="back_in_home_page", on_click=on_clicks.to_home_page),
        state=DialogUser.exit,
    )
)


# is_stop_download_comments = False
# async def to_cancel_downoload(c: CallbackQuery, button: Button, manager: DialogManager):
#     global is_stop_download_comments
#     is_stop_download_comments = True
#     # TODO: тут он должен после смены флага стопорнуться
#     await manager.dialog().switch_to(DialogUser.analysis)
# async def to_download(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.downoland_comments)
#     """Для загрузки кросбара"""
#     asyncio.create_task(background(c, manager.bg()))
# async def analysis_sentiment_result(dialog_manager: DialogManager, **kwargs):
#     check, user_id = authorization.get_authed_user_id(dialog_manager.event.from_user.id)
#     check_credits = database.user.get_user_credits(user_id) >= 1
#     if check_credits:
#         teleid = dialog_manager.event.from_user.id
#
#         database.user.decrease_user_credits(user_id, 1)
#
#         comments = get_variable_from_dict(teleid, UserVariable.comments_array)
#         type_of_grouping = get_variable_from_dict(teleid, UserVariable.type_of_grouping)
#         if get_variable_from_dict(teleid, UserVariable.is_in_loop):
#             start_date = get_variable_from_dict(teleid, UserVariable.analysis_first_date_selected)
#             end_date = get_variable_from_dict(teleid, UserVariable.analysis_second_date_selected)
#         else:
#             start_date, end_date = None, None
#         image_path = sentiment_analysis.make_sentiment_analysis_hist(comments, type_of_grouping, start_date, end_date, str(teleid))
#
#         #await dialog_manager.switch_to(DialogUser.analysis_sentiment_result)
#
#         photo = open(image_path, 'rb')
#         #await dialog_manager.event.bot.(disend_photoalog_manager.event.from_user.id, photo)
#         photo.close()
#     else:
#         await dialog_manager.event.answer("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
#         await dialog_manager.dialog().switch_to(DialogUser.choose_analysis)
# async def to_analysis_first_date_selected(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)
# async def to_back_in_favorites(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.favorites)
# async def to_help(c: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.dialog().switch_to(DialogUser.help)
