import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '5572095516:AAETyYlnp4ysE3ERvcfwj8dTsG4MEeT20zY'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    await bot.send_message(message.chat.id, message.__str__())

executor.start_polling(dp, skip_updates=True)
