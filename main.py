import logging
from aiogram import Bot, Dispatcher, executor, types
from youtube_parser import scrap_comments
import config

API_TOKEN = config.telegram_bot_token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    await bot.send_message(message.chat.id, message.__str__())


@dp.message_handler()
async def scrap(message):
    await bot.send_message(message.chat.id, f'Начинаю обработку...')
    arr = scrap_comments(message.text)
    small = arr[:5]
    await bot.send_message(message.chat.id, f'Получено комментариев: {len(arr)}\n{arr[:5]}')


executor.start_polling(dp, skip_updates=True)
