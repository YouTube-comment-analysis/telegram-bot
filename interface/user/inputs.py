from aiogram_dialog import DialogManager
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram.types import Message

from analysis import word_cloud, phrases_pie_analysis, phrases_plot_analysis
from authorization_process import authorization
from authorization_process.password_encryption import is_correct_password
from database_interaction import database
from database_interaction.auth import get_password, get_user_login
from database_interaction.promocode import use_promocode
from interface.user import user_variable_storage, auxiliary
from interface.FSM import DialogUser
from interface.user.auxiliary import reshow_message
from interface.user.user_variable_storage import add_variable_in_dict, get_variable_from_dict, UserVariable
from scraping import getting_information
from authorization_process.auth import get_authed_user_id, change_password


async def input_url_channel_to_add_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if getting_information.is_channel_url_correct(url):
        id = url.split('www.youtube.com/')[1]
        if id in database.favorite.get_favorite_user_channels(user_id):
            await m.answer(f"Этот канал уже в вашем избранном... ")
        else:
            database.favorite.add_favorite_user_channel(user_id, id)
            await m.answer(f"Ваш канал добавлен в избранное!")
        await manager.dialog().switch_to(DialogUser.favorites_channel)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.add_channel_in_favorites)


async def input_url_channel_to_delete_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                   manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if getting_information.is_channel_url_correct(url):
        id = url.split('www.youtube.com/')[1]
        if id in database.favorite.get_favorite_user_channels(user_id):
            database.favorite.delete_favorite_user_channel(user_id, id)
            await m.answer(f"Ваш канал удален из избранного!")
        else:
            await m.answer(f"Этого канала нет в вашем избранном... ")
        await manager.dialog().switch_to(DialogUser.favorites_channel)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.delete_channel_in_favorites)


async def promo_handler(m: Message, dialog: ManagedDialogAdapterProto,
                        manager: DialogManager):
    if use_promocode(get_authed_user_id(m.from_user.id)[1], m.text)[0]:
        await m.answer(f"Ваша энергия успешно пополнена!")
        await manager.dialog().switch_to(DialogUser.personal_area)
    else:
        await m.answer(f"Неверный промокод.")
        await manager.dialog().switch_to(DialogUser.activate_promo)


async def input_old_passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    old_salt, old_pwd_hash = get_password(get_user_login(get_authed_user_id(m.from_user.id)[1]))
    if is_correct_password(old_salt, old_pwd_hash, m.text):
        add_variable_in_dict(m.from_user.id, UserVariable.old_passw, m.text)
        await manager.dialog().switch_to(DialogUser.input_new_passw)
    else:
        await m.answer(f"Вы неправильно ввели ваш старый пароль.")
        await manager.dialog().switch_to(DialogUser.input_old_passw)


async def input_new_passw_handler(m: Message, dialog: ManagedDialogAdapterProto,
                                  manager: DialogManager):
    # if change_password(m.from_user.id, old_passw, m.text):
    change_password(m.from_user.id, get_variable_from_dict(m.from_user.id, UserVariable.old_passw), m.text)
    await m.answer(f"Пароль изменен!")
    await manager.dialog().switch_to(DialogUser.personal_area)
    # else:
    #     await m.answer(f"Вы неправильно ввели ваш старый пароль.")
    #     await manager.dialog().switch_to(DialogUser.input_old_passw)


async def input_url_video_to_analysis(m: Message, dialog: ManagedDialogAdapterProto,
                                      manager: DialogManager):
    if getting_information.is_video_url_correct(m.text):
        add_variable_in_dict(m.from_user.id, UserVariable.input_url, m.text)
        add_variable_in_dict(m.from_user.id, UserVariable.is_url_video, True)
        await manager.dialog().switch_to(DialogUser.analysis_param)
    else:
        await m.reply("Это не похоже на ссылку с YouTube...")
        await manager.dialog().switch_to(DialogUser.analysis_video)


async def input_words_result(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    teleid = m.from_user.id
    check, user_id = authorization.get_authed_user_id(teleid)
    if database.user.get_user_credits(user_id) >= 1:
        database.user.decrease_user_credits(user_id, 1)

        await auxiliary.show_pie_or_graph(teleid, m, manager)

        await manager.dialog().switch_to(DialogUser.analysis_result_input_words)
    else:
        await m.reply("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
        await manager.dialog().switch_to(DialogUser.choose_analysis)


async def input_url_channel_to_analysis(m: Message, dialog: ManagedDialogAdapterProto,
                                        manager: DialogManager):
    if getting_information.is_channel_url_correct(m.text):
        add_variable_in_dict(m.from_user.id, UserVariable.input_url, m.text)
        add_variable_in_dict(m.from_user.id, UserVariable.is_url_video, False)
        add_variable_in_dict(manager.event.from_user.id, UserVariable.current_date_interval_state, 0)
        await manager.dialog().switch_to(DialogUser.analysis_first_date_selected)
    else:
        await m.reply("Это не похоже на ссылку с YouTube...")
        await manager.dialog().switch_to(DialogUser.analysis_channel)


async def input_photo_png(m: Message, dialog: ManagedDialogAdapterProto,
                          manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    check_credits = database.user.get_user_credits(user_id) >= 1
    if check_credits:
        await m.reply("Подождите пожалуйста... Мне нужно подумать")

        user_photo = rf'photos\input_{m.from_user.id}.jpg'
        path = fr'photos\output_{m.from_user.id}.png'

        downloaded_photo = await m.photo[-1].download(destination_file=user_photo)
        downloaded_photo.close()

        arr = user_variable_storage.get_variable_from_dict(m.from_user.id, UserVariable.comments_array)
        # arr = database.comment.extract_comments(
        #     get_variable_from_dict(m.from_user.id, UserVariable.input_url).split('https://www.youtube.com/watch?v=')[1],
        #     False)

        word_cloud.create_adoptive_background_word_cloud(arr, user_photo, path)

        photo = open(path, 'rb')
        await m.bot.send_photo(m.chat.id, photo)
        photo.close()
        await reshow_message(manager)

        await manager.dialog().switch_to(DialogUser.analysis_result_word_cloud)
        database.user.decrease_user_credits(user_id, 1)
    else:
        await m.reply("Плотите деняг..кхм, не дам я тебе анализ.\nP.S. Платить надо менеджеру")
        await manager.dialog().switch_to(DialogUser.choose_analysis)
        # os.remove(path)
        # os.remove(удалить загрузочный файл)


async def input_url_video_to_add_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                              manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if getting_information.is_video_url_correct(url):
        id = url.split('watch?v=')[1]
        if id not in database.favorite.get_favorite_user_videos(user_id):
            database.favorite.add_favorite_user_video(user_id, id)
            await m.answer(f"Ваше видео добавлено в избранное!")
        else:
            await m.answer(f"Это видео уже есть в избранном.")
        await manager.dialog().switch_to(DialogUser.favorites_video)
    else:
        await m.answer(f"Это не похоже на ссылку с YouTube... ")
        await manager.dialog().switch_to(DialogUser.add_video_in_favorites)


async def input_url_video_to_delete_in_favorites(m: Message, dialog: ManagedDialogAdapterProto,
                                                 manager: DialogManager):
    check, user_id = authorization.get_authed_user_id(m.from_user.id)
    url = m.text
    if getting_information.is_video_url_correct(url):
        id = url.split('watch?v=')[1]
        if id in database.favorite.get_favorite_user_videos(user_id):
            database.favorite.delete_favorite_user_video(user_id, id)
            await m.answer(f"Ваше видео из избранного удалено!")
            await manager.dialog().switch_to(DialogUser.favorites_video)
        else:
            await m.answer(f"Этого видео нет в вашем избранном... ")
            await manager.dialog().switch_to(DialogUser.delete_video_in_favorites)
    else:
        await m.answer(f"Это не похоже на ссылку... ")
        await manager.dialog().switch_to(DialogUser.delete_video_in_favorites)