from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import config

bot = Bot(token=config.telegram_bot_token)


# State machine for guest registration

class FSMGuest(StatesGroup):
    user_id = 0
    credits = 5
    first_name = State()
    last_name = State()
    middle_name = State()
    phone = State()


async def start_of_registration(message: types.Message):
    FSMGuest.user_id = message.chat.id
    await bot.send_message(message.chat.id,
                           'Приветствую гость!\nВам необходимо зарегистрироваться, иначе вы не сможете воспользоваться функциями бота.',
                           reply_markup=types.InlineKeyboardMarkup().add(
                               types.InlineKeyboardButton(text='Зарегистрироваться',
                                                          callback_data='registration_button')))


# Обработчик кнопки "Зарегистрироваться"
async def call_registration_button(callback_query: types.CallbackQuery):
    await FSMGuest.first_name.set()
    await bot.send_message(callback_query.from_user.id, 'Введите ваше имя',
                           reply_markup=types.InlineKeyboardMarkup().add(
                               types.InlineKeyboardButton(text='Отмена',
                                                          callback_data='cancel_button')))


# Выход из состояния
async def call_cancel_button(callback_query: types.CallbackQuery, state: FSMContext):
    curren_state = await state.get_state()
    if curren_state is not None:
        await state.finish()
        await bot.answer_callback_query(
            callback_query.id,
            text='Регистрация отменена', show_alert=True)


# Ловим текст - имя, и записываем его в СЛОВАРЬ
async def get_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите вашу фамилию.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - фамилию, и записываем его в СЛОВАРЬ
async def get_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите ваше отчество.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - отчество, и записываем его в СЛОВАРЬ
async def get_middle_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['middle_name'] = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите ваш номер.\nВ данном формате: 89012345678",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - номер телeфона, и записываем его в СЛОВАРЬ, и заканчиваем регистрацию
async def get_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await message.reply("Регистрация выполнена.")
    await state.finish()


# Регистрируем хендлеры
def register_handlers_guest(dp: Dispatcher):
    dp.register_message_handler(start_of_registration, commands='start', state=None)
    dp.register_callback_query_handler(call_registration_button, text='registration_button')
    dp.register_callback_query_handler(call_cancel_button, state="*", text='cancel_button')
    dp.register_message_handler(get_first_name, state=FSMGuest.first_name)
    dp.register_message_handler(get_last_name, state=FSMGuest.last_name)
    dp.register_message_handler(get_middle_name, state=FSMGuest.middle_name)
    dp.register_message_handler(get_phone, state=FSMGuest.phone)
