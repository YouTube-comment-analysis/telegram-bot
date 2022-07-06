from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import config

bot = Bot(token=config.telegram_bot_token)


# State machine for guest registration

class FSMGuest(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    email = State()
    phone = State()


questCabinet = UserCabinet(0, "Пусто", "Пусто", "Пусто", "Пусто", "Пусто", 5)


async def start_of_registration(message: types.Message):
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
            text='Регистрация отменена.', show_alert=True)


# Ловим текст - имя, и записываем его в СЛОВАРЬ
async def get_first_name(message: types.Message, state: FSMContext):
    questCabinet.first_name = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите вашу фамилию.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - фамилию, и записываем его в СЛОВАРЬ
async def get_last_name(message: types.Message, state: FSMContext):
    questCabinet.last_name = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите ваше отчество.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - отчество, и записываем его в СЛОВАРЬ
async def get_middle_name(message: types.Message, state: FSMContext):
    questCabinet.middle_name = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите ваш email",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - эл. почту, и записываем его в СЛОВАРЬ
async def get_email(message: types.Message, state: FSMContext):
    questCabinet.email = message.text
    await FSMGuest.next()
    await message.reply("Теперь введите ваш номер.\nВ данном формате: 89012345678",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(text='Отмена',
                                                       callback_data='cancel_button')))


# Ловим текст - номер телeфона, и записываем его в СЛОВАРЬ, потом все отправляем в БД и заканчиваем регистрацию
async def get_phone(message: types.Message, state: FSMContext):
    questCabinet.phone = message.text
    questCabinet.telegram_id = message.chat.id
    register_user(questCabinet.telegram_id, UserRole.user, questCabinet)
    await message.reply(
        f"Регистрация выполнена: {user_exists(questCabinet.telegram_id)}. Пожалуйста ведите команду /start (если не сработает /home_page)")
    await state.finish()


# Регистрируем хендлеры
def register_handlers_guest(dp: Dispatcher):
    dp.register_message_handler(start_of_registration, state=None)
    dp.register_callback_query_handler(call_registration_button, text='registration_button')
    dp.register_callback_query_handler(call_cancel_button, state="*", text='cancel_button')
    dp.register_message_handler(get_first_name, state=FSMGuest.first_name)
    dp.register_message_handler(get_last_name, state=FSMGuest.last_name)
    dp.register_message_handler(get_middle_name, state=FSMGuest.middle_name)
    dp.register_message_handler(get_email, state=FSMGuest.email)
    dp.register_message_handler(get_phone, state=FSMGuest.phone)
