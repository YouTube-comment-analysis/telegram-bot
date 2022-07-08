import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram_dialog import DialogRegistry

import config
from interface.FSM import DialogUser
from interface.authorization_or_registration import start, dialog_start
from interface.user import dialog_user

src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))

API_TOKEN = config.telegram_bot_token


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    dp.register_message_handler(start, text="/start", state="*")
    # dp.register_message_handler(settings, text="/settings", state=DialogUser.all_states) - не работает
    registry = DialogRegistry(dp)
    registry.register(dialog_start)
    registry.register(dialog_user)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
