from aiogram.dispatcher.filters.state import StatesGroup, State


class DialogSign(StatesGroup):
    start = State()  # состояния для начального входа в программу
    input_name = State()
    input_surname = State()
    input_patronymic = State()
    input_phone = State()
    input_email = State()
    input_log_reg = State()
    input_passw_reg = State()
    return_input_passw_reg = State()
    registration_status = State()
    input_login_auth = State()
    input_password_auth = State()
    login_status = State()
    home_page = State()


class DialogUser(StatesGroup):
    home_page = State()
    #состояния для личного кабинета
    personal_area = State()
    activate_promo = State()
    input_old_passw = State()
    input_new_passw = State()
    # состояния для анализа
    analysis = State()
    analysis_video = State()
    analysis_channel = State()
    filter_analysis = State()
    analysis_first_date_selected = State()
    analysis_second_date_selected = State()
    analysis_param = State()
    analysis_db = State()
    downoland_comments = State()
    # not_pump_up = State()
    # pump_up = State()
    # состояния для избранного
    favorites = State()
    favorites_video = State()
    favorites_channel = State()
    view_all_video_in_favorites = State()
    add_video_in_favorites = State()
    delete_video_in_favorites = State()
    view_all_channel_in_favorites = State()
    add_channel_in_favorites = State()
    delete_channel_in_favorites = State()
    # состояния для истории
    history = State()
    history_video = State()
    view_all_video_in_history = State()
    history_channel = State()
    view_all_channel_in_history = State()
    # состояния для помощи
    help = State()
    # состояния для настройки - не работает
    settings = State()
    # состояния для выхода
    exit = State()


class DialogAdmin(StatesGroup):
    start = State()  # состояния для начального входа в программу


class DialogMngr(StatesGroup):
    start = State()  # состояния для начального входа в программу
    get_login_to_give_energy = State()
    give_energy = State()
