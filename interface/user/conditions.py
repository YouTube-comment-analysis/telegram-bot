from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.when import Whenable
from typing import Dict

from database_interaction.user import get_user_role, UserRole
from interface.user import user_variable_storage
from interface.user.user_variable_storage import UserVariable
from authorization_process.auth import get_authed_user_id


def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    user_id = get_authed_user_id(telegram_id)[1]
    return get_user_role(user_id) == UserRole.admin


def is_manager(data: Dict, widget: Whenable, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    user_id = get_authed_user_id(telegram_id)[1]
    return get_user_role(user_id) == UserRole.manager


def is_graph(data: Dict, widget: Whenable, manager: DialogManager):
    return not user_variable_storage.get_variable_from_dict(manager.event.from_user.id, UserVariable.is_chart_pie)