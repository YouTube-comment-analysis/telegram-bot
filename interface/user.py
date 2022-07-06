from aiogram import types, Bot
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

bot = Bot(token=config.telegram_bot_token)


class FSMUser(StatesGroup):
    activate_promo = State()
    analysis_video = State()
    analysis_channel = State()
    favorites_video = State()
    favorites_channel = State()
    view_all_video = State()
    view_all_channel = State()
    add_video_in_favorites = State()
    delete_video_in_favorites = State()
    add_channel_in_favorites = State()
    delete_channel_in_favorites = State()
    history_video = State()
    view_all_video_in_history = State()
    history_channel = State()
    view_all_channel_in_history = State()


# Главная клавиатура
main_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Личный кабинет', callback_data='personal_area_button'),
    InlineKeyboardButton(text='Проанализировать', callback_data='analysis_button'),
    InlineKeyboardButton(text='Избранное', callback_data='favorites_button'),
    InlineKeyboardButton(text='Помощь', callback_data='help_button'),
    InlineKeyboardButton(text='История', callback_data='history_button'),
    InlineKeyboardButton(text='Выход', callback_data='exit_button'))

# Для Главной страницы сообщение от бота
msg_main = "Добро пожаловать на главную страницу!"

# Для Личного кабинета клавиатура
personal_account_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Активировать промокод', callback_data='activate_promo_code_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для Личного кабинета текст сообщения от бота
msg_personal_account = "Личный кабинет" \
                       "\nВаша роль: {role.name}" \
                       "\nВаше имя: {cab.first_name}" \
                       "\nВаша фамилия: {cab.last_name}" \
                       "\nВаше отчество: {cab.middle_name}" \
                       "\nВаш номер телефона: {cab.phone}" \
                       "\nВаш email: {cab.email}" \
                       "\nКол-во энергии: {cab.credits}"

# Для Анализа текст сообщения от бота
msg_analysis = "Что хотите проанализировать?" \
               "\nЗАМЕЧАНИЕ: Анализ будет произведен максимум для {???} комментариев"

# Для Анализа клавиатура
analysis_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Анализ видео', callback_data='analysis_video_button'),
    InlineKeyboardButton(text='Анализ канала', callback_data='analysis_channel_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для Избранного текст сообщения от бота
msg_favorites = "Какие избранные хотите просмотреть?"

# Для Избранного клавиатура
favorites_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Видео', callback_data='favorites_video_button'),
    InlineKeyboardButton(text='Каналы', callback_data='favorites_channel_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для 5 последних - Избранного видео/канала текст сообщения
msg_favorites_short_list = "\nVVVVVVVVVVVV" \
                           "\nVVVVVVVVVVVV" \
                           "\nVVVVVVVVVVVV" \
                           "\nVVVVVVVVVVVV" \
                           "\nVVVVVVVVVVVV"

# Для всех - Избранного видео/канала текст сообщения
msg_favorites_long_list = "\nVVVVVVVVVVVV" \
                          "\nVVVVVVVVVVVV" \
                          "\nVVVVVVVVVVVV" \
                          "\n............" \
                          "\nVVVVVVVVVVVV"

# Для 5 последних - Избранного видео клавиатура
favorites_short_list_video_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Просмотреть всё', callback_data='view_all_video_button'),
    InlineKeyboardButton(text='Добавить по ссылке в избранного', callback_data='add_video_to_favorites_button'),
    InlineKeyboardButton(text='Удалить по ссылке из избранного', callback_data='delete_video_from_favorites_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для 5 последних - Избранного канала клавиатура
favorites_short_list_channel_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Просмотреть всё', callback_data='view_all_channel_button'),
    InlineKeyboardButton(text='Добавить по ссылке в избранного', callback_data='add_channel_to_favorites_button'),
    InlineKeyboardButton(text='Удалить по ссылке из избранного', callback_data='delete_channel_from_favorites_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для Истории текст сообщения от бота
msg_history = "Какую историю хотите просмотреть?"

# Для Истории клавиатура
history_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Видео', callback_data='history_video_button'),
    InlineKeyboardButton(text='Каналы', callback_data='history_channel_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для 5 последних - истории видео/канала текст сообщения
msg_history_short_list = "\nVVVVVVVVVVVV" \
                         "\nVVVVVVVVVVVV" \
                         "\nVVVVVVVVVVVV" \
                         "\nVVVVVVVVVVVV" \
                         "\nVVVVVVVVVVVV"

# Для всех - истории видео/канала текст сообщения
msg_history_long_list = "\nVVVVVVVVVVVV" \
                        "\nVVVVVVVVVVVV" \
                        "\nVVVVVVVVVVVV" \
                        "\n............" \
                        "\nVVVVVVVVVVVV"

# Для 5 последних - истории видео клавиатура
history_short_list_video_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Просмотреть всё', callback_data='view_all_video_history_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))

# Для 5 последних - истории канала клавиатура
history_short_list_channel_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Просмотреть всё', callback_data='view_all_channel_history_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))


# State machine for user home page

async def start_home(message: types.Message):
    await bot.send_message(message.chat.id, msg_main, reply_markup=main_kb)


# Обработчик кнопки "Личный кабинет"
async def personal_area_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text=msg_personal_account, reply_markup=personal_account_kb)


# Обрабатываем ВСЕ кнопки "Назад" и кнопку "Ок"
async def call_back_button(callback_query: types.CallbackQuery, state: FSMContext):
    curren_state = await state.get_state()
    if curren_state is None:
        await callback_query.message.edit_text(text=msg_main, reply_markup=main_kb)
        # await state.reset_state()
    elif curren_state == 'FSMUser:favorites_video' or curren_state == 'FSMUser:favorites_channel':
        await callback_query.message.edit_text(text=msg_favorites, reply_markup=favorites_kb)
        await state.reset_state()
    elif curren_state == 'FSMUser:history_channel' or curren_state == 'FSMUser:history_video':
        await callback_query.message.edit_text(text=msg_history, reply_markup=history_kb)
        await state.reset_state()
    elif curren_state == 'FSMUser:view_all_video':
        await callback_query.message.edit_text(text="Список 5 последних избранных ВИДЕО:" + msg_favorites_short_list,
                                               reply_markup=favorites_short_list_video_kb)
        await FSMUser.favorites_video.set()
    elif curren_state == 'FSMUser:view_all_channel':
        await callback_query.message.edit_text(text="Список 5 последних избранных КАНАЛОВ:" + msg_favorites_short_list,
                                               reply_markup=favorites_short_list_channel_kb)
        await FSMUser.favorites_channel.set()
    elif curren_state == 'FSMUser:view_all_channel_in_history':
        await callback_query.message.edit_text(text="Список 5 последних КАНАЛОВ в истории:" + msg_history_short_list,
                                               reply_markup=history_short_list_channel_kb)
        await FSMUser.history_channel.set()
    elif curren_state == 'FSMUser:view_all_video_in_history':
        await callback_query.message.edit_text(text="Список 5 последних ВИДЕО в истории:" + msg_history_short_list,
                                               reply_markup=history_short_list_video_kb)
        await FSMUser.history_video.set()


# Обрабатываем кнопку "Активировать промокод"
async def call_activate_promo_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.activate_promo.set()
    await callback_query.message.edit_text(text="Введите промокод",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Выход из состояния активации промокода, обрабатываем ВСЕ кнопки "Отмена"
async def call_cancel_button(callback_query: types.CallbackQuery, state: FSMContext):
    curren_state = await state.get_state()
    if curren_state is not None:
        # Найти как сравнивать состояния..
        if curren_state == 'FSMUser:activate_promo':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение промокода отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_personal_account, reply_markup=personal_account_kb)
            await state.reset_state()
        elif curren_state == 'FSMUser:analysis_video':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение URL видео отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_analysis, reply_markup=analysis_kb)
            await state.reset_state()
        elif curren_state == 'FSMUser:analysis_channel':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение URL канала отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_analysis, reply_markup=analysis_kb)
            await state.reset_state()
        elif curren_state == 'FSMUser:add_video_in_favorites':
            await bot.answer_callback_query(
                callback_query.id,
                text='Ввод URL видео для добавления отменено', show_alert=True)
            await callback_query.message.edit_text(
                text="Список 5 последних избранных ВИДЕО:" + msg_favorites_short_list,
                reply_markup=favorites_short_list_video_kb)
            await FSMUser.favorites_video.set()
        elif curren_state == 'FSMUser:delete_video_in_favorites':
            await bot.answer_callback_query(
                callback_query.id,
                text='Ввод URL видео для удаления отменено', show_alert=True)
            await callback_query.message.edit_text(
                text="Список 5 последних избранных ВИДЕО:" + msg_favorites_short_list,
                reply_markup=favorites_short_list_video_kb)
            await FSMUser.favorites_video.set()
        elif curren_state == 'FSMUser:add_channel_in_favorites':
            await bot.answer_callback_query(
                callback_query.id,
                text='Ввод URL канала для добавления отменено', show_alert=True)
            await callback_query.message.edit_text(
                text="Список 5 последних избранных КАНАЛОВ:" + msg_favorites_short_list,
                reply_markup=favorites_short_list_channel_kb)
            await FSMUser.favorites_channel.set()
        elif curren_state == 'FSMUser:delete_channel_in_favorites':
            await bot.answer_callback_query(
                callback_query.id,
                text='Ввод URL канала для удаления отменено', show_alert=True)
            await callback_query.message.edit_text(
                text="Список 5 последних избранных КАНАЛОВ:" + msg_favorites_short_list,
                reply_markup=favorites_short_list_channel_kb)
            await FSMUser.favorites_channel.set()


# Ловим текст - промокод
async def get_promo_and_give_credits(message: types.Message, state: FSMContext):
    if '1' == message.text:  # '1' это номер промокода
        await bot.send_message(message.chat.id, "Энергия пополнена", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='ОК',
                                       callback_data='back_button')))
        await state.reset_state()
    else:
        await bot.send_message(message.chat.id, "Неверный промокод", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Отмена',
                                       callback_data='cancel_button')))


# Обработчик кнопки "Проанализировать"
async def call_analysis_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text=msg_analysis, reply_markup=analysis_kb)


# Обрабатываем кнопку "Анализ видео"
async def call_analysis_video_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.analysis_video.set()
    await callback_query.message.edit_text(text="Введите URL видео.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Обрабатываем кнопку "Анализ канала"
async def call_analysis_channel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.analysis_channel.set()
    await callback_query.message.edit_text(text="Введите URL канала.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Обработчик кнопки "Избранное"
async def call_favorites_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text=msg_favorites, reply_markup=favorites_kb)


# Обрабатываем кнопку "Избранные видео"
async def call_favorites_video_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.favorites_video.set()
    await callback_query.message.edit_text(
        text="Список 5 последних избранных ВИДЕО:" + msg_favorites_short_list,
        reply_markup=favorites_short_list_video_kb)


# Обрабатываем кнопку "Просмотреть все" ВИДЕО
async def call_view_all_video_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.view_all_video.set()
    await callback_query.message.edit_text(
        text="Список всех избранных ВИДЕО:" + msg_favorites_long_list,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Назад',
                                       callback_data='back_button')))


# Обрабатываем кнопку "Добавить видео в избранное"
async def call_add_video_in_favorites_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.add_video_in_favorites.set()
    await callback_query.message.edit_text(text="Введите URL видео которое хотите добавить.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Ловим текст - URL видео для добавления в избранное
async def get_url_video_and_add_to_favorites(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Видео добавлено в избранное: {True}",
                           reply_markup=types.InlineKeyboardMarkup().add(
                               types.InlineKeyboardButton(text='ОК',
                                                          callback_data='back_button')))
    await FSMUser.favorites_video.set()


# Обрабатываем кнопку "Удалить видео из избранного"
async def call_delete_video_in_favorites_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.delete_video_in_favorites.set()
    await callback_query.message.edit_text(text="Введите URL видео которое хотите удалить.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Обрабатываем кнопку "Избранные каналы"
async def call_favorites_channel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.favorites_channel.set()
    await callback_query.message.edit_text(
        text="Список 5 последних избранных КАНАЛОВ:" + msg_favorites_short_list,
        reply_markup=favorites_short_list_channel_kb)


# Обрабатываем кнопку "Просмотреть все" КАНАЛЫ
async def call_view_all_channel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.view_all_channel.set()
    await callback_query.message.edit_text(
        text="Список всех избранных КАНАЛОВ:" + msg_favorites_long_list,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Назад',
                                       callback_data='back_button')))


# Обрабатываем кнопку "Добавить канал в избранное"
async def call_add_channel_in_favorites_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.add_channel_in_favorites.set()
    await callback_query.message.edit_text(text="Введите URL канала которое хотите добавить.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Ловим текст - URL канала для добавления в избранное
async def get_url_channel_and_add_to_favorites(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Канал добавлен в избранное: {True}",
                           reply_markup=types.InlineKeyboardMarkup().add(
                               types.InlineKeyboardButton(text='ОК',
                                                          callback_data='back_button')))
    await FSMUser.favorites_video.set()


# Обрабатываем кнопку "Удалить канал из избранного"
async def call_delete_channel_in_favorites_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.delete_channel_in_favorites.set()
    await callback_query.message.edit_text(text="Введите URL канала которое хотите удалить.",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Обработчик кнопки "Помощь"
async def help_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text="Данный бот может:"
                                                "\n1)................"
                                                "\n2)................"
                                                "\n3)................"
                                                "\nКоманды для бота:"
                                                "\n/start - запуск бота"
                                                "\nБыстрые перемещения:"
                                                "\n/home_page - домашняя страница (главная)"
                                                "\n/analysis - анализ"
                                                "\n/favorites - избранные URL"
                                                "\n/history - история запросов",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Назад',
                                                                          callback_data='back_button')))


# Обработчик кнопки "История"
async def history_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text=msg_history, reply_markup=history_kb)


# Обрабатываем кнопку "История видео"
async def call_history_video_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.history_video.set()
    await callback_query.message.edit_text(
        text="Список 5 последних ВИДЕО в истории:" + msg_history_short_list,
        reply_markup=history_short_list_video_kb)


# Обрабатываем кнопку "Просмотреть все" ВИДЕО В ИСТОРИИ
async def call_view_all_video_history_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.view_all_video_in_history.set()
    await callback_query.message.edit_text(
        text="Список всех ВИДЕО в истории:" + msg_history_long_list,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Назад',
                                       callback_data='back_button')))


# Обрабатываем кнопку "История каналы"
async def call_history_channel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.history_channel.set()
    await callback_query.message.edit_text(
        text="Список 5 последних КАНАЛОВ в истории:" + msg_history_short_list,
        reply_markup=history_short_list_channel_kb)


# Обрабатываем кнопку "Просмотреть все" КАНАЛЫ В ИСТОРИИ
async def call_view_all_channel_history_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.view_all_channel_in_history.set()
    await callback_query.message.edit_text(
        text="Список всех КАНАЛОВ в истории:" + msg_history_long_list,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Назад',
                                       callback_data='back_button')))


# Регистрируем хендлеры
def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_home, commands='home_page', state=None)
    dp.register_callback_query_handler(personal_area_button, text='personal_area_button')
    dp.register_callback_query_handler(call_back_button, state="*", text='back_button')
    dp.register_callback_query_handler(call_activate_promo_button, text='activate_promo_code_button')
    dp.register_callback_query_handler(call_cancel_button, state="*", text='cancel_button')
    dp.register_message_handler(get_promo_and_give_credits, state=FSMUser.activate_promo)
    dp.register_callback_query_handler(call_analysis_button, text='analysis_button')
    dp.register_callback_query_handler(call_analysis_video_button, text='analysis_video_button')
    dp.register_callback_query_handler(call_analysis_channel_button, text='analysis_channel_button')
    dp.register_callback_query_handler(call_favorites_button, text='favorites_button')
    dp.register_callback_query_handler(call_favorites_video_button, text='favorites_video_button')
    dp.register_callback_query_handler(call_view_all_video_button, state=FSMUser.favorites_video,
                                       text='view_all_video_button')
    dp.register_callback_query_handler(call_add_video_in_favorites_button, state=FSMUser.favorites_video,
                                       text='add_video_to_favorites_button')
    dp.register_message_handler(get_url_video_and_add_to_favorites, state=FSMUser.add_video_in_favorites)
    dp.register_callback_query_handler(call_delete_video_in_favorites_button, state=FSMUser.favorites_video,
                                       text='delete_video_from_favorites_button')
    dp.register_callback_query_handler(call_favorites_channel_button, text='favorites_channel_button')
    dp.register_callback_query_handler(call_view_all_channel_button, state=FSMUser.favorites_channel,
                                       text='view_all_channel_button')
    dp.register_callback_query_handler(call_add_channel_in_favorites_button, state=FSMUser.favorites_channel,
                                       text='add_channel_to_favorites_button')
    dp.register_message_handler(get_url_channel_and_add_to_favorites, state=FSMUser.add_channel_in_favorites)
    dp.register_callback_query_handler(call_delete_channel_in_favorites_button, state=FSMUser.favorites_channel,
                                       text='delete_channel_from_favorites_button')
    dp.register_callback_query_handler(help_button, text='help_button')
    dp.register_callback_query_handler(history_button, text='history_button')
    dp.register_callback_query_handler(call_history_video_button, text='history_video_button')
    dp.register_callback_query_handler(call_view_all_video_history_button, state=FSMUser.history_video,
                                       text='view_all_video_history_button')
    dp.register_callback_query_handler(call_history_channel_button, text='history_channel_button')
    dp.register_callback_query_handler(call_view_all_channel_history_button, state=FSMUser.history_channel,
                                       text='view_all_channel_history_button')
