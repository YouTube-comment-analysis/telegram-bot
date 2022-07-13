from aiogram_dialog import DialogManager
from aiogram.types import Message

from interface.FSM import DialogUser
from interface.user.user_variable_storage import clear_user_variable_space


async def settings(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.settings)  # это костыль, разработчик библиотеки предложил его
    # await dialog_manager.switch_to(DialogUser.settings)


async def helps(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.help)  # это костыль, разработчик библиотеки предложил его


async def home_page(m: Message, dialog_manager: DialogManager):
    clear_user_variable_space(dialog_manager.event.from_user.id)
    await dialog_manager.bg().switch_to(DialogUser.home_page)  # это костыль, разработчик библиотеки предложил его


async def analyse(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.analysis)  # это костыль, разработчик библиотеки предложил его


async def history(m: Message, dialog_manager: DialogManager):
    await dialog_manager.bg().switch_to(DialogUser.history)  # это костыль, разработчик библиотеки предложил его