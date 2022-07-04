import logging

from aiogram import Bot, Dispatcher, executor
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from interface.guest import register_handlers_guest

storage = MemoryStorage()
API_TOKEN = config.telegram_bot_token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

register_handlers_guest(dp)


@dp.message_handler(state=None)
async def renewal(message):
    await bot.send_message(message.chat.id, 'Введите команду /start')


executor.start_polling(dp, skip_updates=True)
