import logging
from aiogram import Bot, Dispatcher, executor
import config
from database_interaction.user import get_user_role, UserRole, user_exists
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from interface.guest import register_handlers_guest
from interface.user import register_handlers_user

API_TOKEN = config.telegram_bot_token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def renewal(message):
    if not user_exists(message.chat.id):
        await bot.send_message(message.chat.id, 'Введите команду /home_page')
        register_handlers_guest(dp)
    elif get_user_role(message.chat.id) == UserRole.user:
        await bot.send_message(message.chat.id, 'Введите команду /home_page')
        register_handlers_user(dp)
    elif get_user_role(message.chat.id) == UserRole.admin:
        await bot.send_message(message.chat.id, 'Введите команду /home_page')
        # register_handlers_admin(dp)
    elif get_user_role(message.chat.id) == UserRole.manager:
        await bot.send_message(message.chat.id, 'Введите команду /home_page')
        # register_handlers_manager(dp)
    elif get_user_role(message.chat.id) == UserRole.banned:
        await bot.send_message(message.chat.id, 'Извините, ваш аккаунт забанен')


executor.start_polling(dp, skip_updates=True)
