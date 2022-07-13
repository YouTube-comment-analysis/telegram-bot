import aiogram.types
from aiogram_dialog import DialogManager
from aiogram.types import Message

from analysis import phrases_pie_analysis, phrases_plot_analysis
from interface.FSM import DialogUser
from interface.user.user_variable_storage import get_variable_from_dict, UserVariable, add_variable_in_dict


async def reshow_message(manager: DialogManager):
    message = manager.event if isinstance(manager.event, aiogram.types.Message) else manager.event.message
    await manager.event.bot.delete_message(message.chat.id, message.message_id)
    await manager.switch_to(DialogUser.analysis_sentiment_show_result)


async def show_pie_or_graph(teleid: int, m: Message, manager: DialogManager):
    comments = get_variable_from_dict(teleid, UserVariable.comments_array)

    # TODO: замечание того, что фото должно обновляться в зависимости от даты (когда нажата кнопка "обновить")
    is_order_matter = get_variable_from_dict(teleid, UserVariable.is_order_matter)

    #брать выбранный пользователем интреврал или весь доступный интервал
    if get_variable_from_dict(teleid, UserVariable.is_in_loop):
        phrases = get_variable_from_dict(teleid, UserVariable.phrases)
        start_date = get_variable_from_dict(teleid, UserVariable.analysis_first_date_selected)
        end_date = get_variable_from_dict(teleid, UserVariable.analysis_second_date_selected)
    else:
        phrases = m.text.split(',')
        add_variable_in_dict(teleid, UserVariable.phrases, phrases)
        start_date, end_date = None, None

    if get_variable_from_dict(teleid, UserVariable.is_chart_pie):
        image_path = phrases_pie_analysis.make_word_count_analysis_pie(comments, phrases, is_order_matter, start_date, end_date, str(teleid))
    else:
        type_of_grouping = get_variable_from_dict(teleid, UserVariable.type_of_grouping)
        image_path = phrases_plot_analysis.make_word_count_analysis_plot(comments, phrases, type_of_grouping, is_order_matter, start_date, end_date, str(teleid))

    photo = open(image_path, 'rb')
    await m.bot.send_photo(m.chat.id, photo)
    photo.close()
    await reshow_message(manager)