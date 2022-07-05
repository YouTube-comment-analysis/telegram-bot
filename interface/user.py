from aiogram import types, Bot
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from database_interaction.user import get_user_role, UserRole, get_user_cabinet, update_user_credits

bot = Bot(token=config.telegram_bot_token)


class FSMUser(StatesGroup):
    activate_promo = State()


# Главная клавиатура
main_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Личный кабинет', callback_data='personal_area_button'),
    InlineKeyboardButton(text='Проанализировать', callback_data='analysis_button'),
    InlineKeyboardButton(text='Избранное', callback_data='favorites_button'),
    InlineKeyboardButton(text='Помощь', callback_data='help_button'),
    InlineKeyboardButton(text='История', callback_data='history_button'))

# Для личного кабинета клавиатура
personal_account_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Активировать промокод', callback_data='activate_promo_code_button'),
    InlineKeyboardButton(text='Назад', callback_data='back_button'))


# State machine for user home page

async def start_home(message: types.Message):
    await bot.send_message(message.chat.id, 'Приветствую пользователь!', reply_markup=main_kb)


# Обработчик кнопки "Личный кабинет"
async def personal_area_button(callback_query: types.CallbackQuery):
    role = get_user_role(callback_query.from_user.id)
    cab = get_user_cabinet(callback_query.from_user.id)
    await callback_query.message.edit_text(
        text=f"Личный кабинет"
             f"\nВаша роль: {role.name}"
             f"\nВаше имя: {cab.first_name}"
             f"\nВаша фамилия: {cab.last_name}"
             f"\nВаше отчество: {cab.middle_name}"
             f"\nВаш номер телефона: {cab.phone}"
             f"\nВаш email: {cab.email}"
             f"\nКол-во энергии: {cab.credits}",
        reply_markup=personal_account_kb)


# Обрабатываем кнопку "Назад"
async def call_back_button(callback_query: types.CallbackQuery, state: FSMContext):
    curren_state = await state.get_state()
    if curren_state is None:
        await callback_query.message.edit_text(text="Приветствую пользователь!", reply_markup=main_kb)


# Обрабатываем кнопку "Активировать промокод"
async def call_activate_promo_button(callback_query: types.CallbackQuery, state: FSMContext):
    await FSMUser.activate_promo.set()
    await callback_query.message.edit_text(text="Введите промокод",
                                           reply_markup=types.InlineKeyboardMarkup().add(
                                               types.InlineKeyboardButton(text='Отмена',
                                                                          callback_data='cancel_button')))


# Выход из состояния активации промокода
async def call_cancel_button(callback_query: types.CallbackQuery, state: FSMContext):
    curren_state = await state.get_state()
    if curren_state is not None:
        await state.finish()
        await bot.answer_callback_query(
            callback_query.id,
            text='Введение промокода отменено', show_alert=True)


# Ловим текст - промокод
async def get_promo_and_give_credits(message: types.Message, state: FSMContext):
    if '1' == message.text:  # '1' это номер промокода
        update_user_credits(message.from_user.id, get_user_cabinet(message.from_user.id).credits + 5)
        await message.reply("Энергия пополнена! Пожалуйста ведите команду /home_page")
        await state.finish()
    else:
        await message.reply("Неверный промокод", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='Отмена',
                                       callback_data='cancel_button')))


# Регистрируем хендлеры
def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_home, state=None)
    dp.register_callback_query_handler(personal_area_button, text='personal_area_button')
    dp.register_callback_query_handler(call_back_button, state="*", text='back_button')
    dp.register_callback_query_handler(call_activate_promo_button, text='activate_promo_code_button')
    dp.register_callback_query_handler(call_cancel_button, state="*", text='cancel_button')
    dp.register_message_handler(get_promo_and_give_credits, state=FSMUser.activate_promo)
    # dp.register_message_handler(get_last_name, state=FSMGuest.last_name)
    # dp.register_message_handler(get_middle_name, state=FSMGuest.middle_name)
    # dp.register_message_handler(get_phone, state=FSMGuest.phone)
