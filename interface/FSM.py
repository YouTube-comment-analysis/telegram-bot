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
    personal_area = State()
    activate_promo = State()
    input_old_passw = State()
    input_new_passw = State()
    # состояния для анализа
    favorites = State()
    favorites_video = State()
    favorites_channel = State()
    view_all_video_in_favorites = State()
    add_video_in_favorites = State()
    delete_video_in_favorites = State()
    view_all_channel_in_favorites = State()
    add_channel_in_favorites = State()
    delete_channel_in_favorites = State()
    history = State()
    history_video = State()
    view_all_video_in_history = State()
    history_channel = State()
    view_all_channel_in_history = State()
    help = State()
    settings = State()
    exit = State()