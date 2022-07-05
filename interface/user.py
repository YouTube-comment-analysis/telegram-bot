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

# Главная клавиатура
main_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Личный кабинет', callback_data='personal_area_button'),
    InlineKeyboardButton(text='Проанализировать', callback_data='analysis_button'),
    InlineKeyboardButton(text='Избранное', callback_data='favorites_button'),
    InlineKeyboardButton(text='Помощь', callback_data='help_button'),
    InlineKeyboardButton(text='История', callback_data='history_button'))

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
        #Найти как сравнивать состояния..
        if curren_state == 'FSMUser:activate_promo':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение промокода отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_personal_account, reply_markup=personal_account_kb)
        elif curren_state == 'FSMUser:analysis_video':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение URL видео отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_analysis, reply_markup=analysis_kb)
        elif curren_state == 'FSMUser:analysis_channel':
            await bot.answer_callback_query(
                callback_query.id,
                text='Введение URL канала отменено', show_alert=True)
            await callback_query.message.edit_text(text=msg_analysis, reply_markup=analysis_kb)
        await state.reset_state()


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
