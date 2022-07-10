from __future__ import print_function
import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram_dialog import DialogRegistry

import config

from interface.FSM import DialogUser
from interface.admin import dialog_admin
from interface.authorization_or_registration import start, dialog_start
from interface.manager import dialog_manager

from interface.user import dialog_user, settings, helps, home_page, analyse, history


src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))

API_TOKEN = config.telegram_bot_token


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    dp.register_message_handler(start, text="/start", state="*")
    #TODO: быстрых перемещений не должно быть в момент загрузки чего либо! Надо изменить состояния
    dp.register_message_handler(settings, text="/settings", aiogd_intent_state_group=DialogUser)
    dp.register_message_handler(home_page, text="/home_page", aiogd_intent_state_group=DialogUser)
    dp.register_message_handler(analyse, text="/analysis", aiogd_intent_state_group=DialogUser)
    dp.register_message_handler(history, text="/history", aiogd_intent_state_group=DialogUser)
    dp.register_message_handler(helps, text="/help", aiogd_intent_state_group=DialogUser)
    registry.register(dialog_start)
    registry.register(dialog_user)
    registry.register(dialog_admin)
    registry.register(dialog_manager)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
