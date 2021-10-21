from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from solidAPI import emoji

from base.player import player
from utils.pyro_utils import music_result
from solidAPI.chat import set_lang
from solidAPI.other import get_message
from pyrogram import Client, filters


def play_next_keyboard(user_id: int):
    i = 5
    for j in range(5):
        i += 1
        yield InlineKeyboardButton(f"{i}", callback_data=f"playnext {j}|{user_id}")
        j += 1


def play_back_keyboard(user_id: int):
    i = 0
    for j in range(5):
        i += 1
        yield InlineKeyboardButton(f"{i}", callback_data=f"play {j}|{user_id}")
        j += 1


@Client.on_callback_query(filters.regex(pattern=r"close"))
async def close_button(_, cb: CallbackQuery):
    callback = cb.data.split("|")
    user_id = int(callback[1])
    message = cb.message
    from_user_id = cb.from_user.id
    chat_id = message.chat.id
    person = await message.chat.get_member(from_user_id)
    if from_user_id != user_id:
        return await cb.answer("this is not for you.", show_alert=True)
    music_result[chat_id].clear()
    if person.status in ["creator", "administrator"]:
        return await message.delete()
    return await message.delete()


@Client.on_callback_query(filters.regex(pattern=r"close2"))
async def close_private_button(_, cb: CallbackQuery):
    return await cb.message.delete()


@Client.on_callback_query(filters.regex(pattern=r"set_lang_(.*)"))
async def change_language_(_, cb: CallbackQuery):
    lang = cb.matches[0].group(1)
    chat = cb.message.chat
    try:
        set_lang(chat.id, lang)
        await cb.edit_message_text(get_message(chat.id, "lang_changed"))
    except Exception as e:
        await cb.edit_message_text(f"an error occured\n\n{e}")


@Client.on_callback_query(filters.regex(pattern=r"play(.*)"))
async def play_music(_, cb: CallbackQuery):
    match = cb.matches[0].group(1)
    data = cb.data.split("|")
    user_id = int(data[1])
    index = int(data[0].split(" ")[1])
    chat_id = cb.message.chat.id
    from_id = cb.from_user.id
    if from_id != user_id:
        return await cb.answer("this is not for u", show_alert=True)

    if not match:
        music = music_result[chat_id][0]
        title: str = music[index]["title"]
        uri: str = music[index]["url"]
        result = {
            "title": title,
            "uri": uri
        }

        music_result[chat_id].clear()
        await player.play(cb, result)
    if match:
        music = music_result[chat_id][1]
        title: str = music[index]["title"]
        uri: str = music[index]["url"]
        result = {
            "title": title,
            "uri": uri
        }
        music_result[chat_id].clear()
        await player.play(cb, result)


@Client.on_callback_query(filters.regex(pattern=r"next"))
async def next_music_(client: Client, cb: CallbackQuery):
    bot_username = (await client.get_me()).username
    user_id = int(cb.data.split("|")[1])
    chat_id = cb.message.chat.id
    music = music_result[chat_id][1]
    results = "\n"
    from_id = cb.from_user.id
    k = 5
    if from_id != user_id:
        return await cb.answer("you not allowed", show_alert=True)

    for i in music:
        k += 1
        results += f"{k}. [{i['title'][:35]}...]({i['url']})\n"
        results += f"┣ {emoji.LIGHT_BULB} duration - {i['duration']}\n"
        results += f"┣ {emoji.FIRE} [More Information](https://t.me/{bot_username}?start=ytinfo_{i['url']})\n\n"

    temp = []
    keyboard = []
    in_keyboard = list(play_next_keyboard(user_id))
    for count, j in enumerate(in_keyboard, start=1):
        temp.append(j)
        if count % 3 == 0:
            keyboard.append(temp)
            temp = []
        if count == len(in_keyboard):
            keyboard.append(temp)
    await cb.edit_message_text(
        f"results\n{results}\n", reply_markup=InlineKeyboardMarkup(
            [
                keyboard[0],
                keyboard[1],
                [
                    InlineKeyboardButton(f"back {emoji.LEFT_ARROW}", f"back|{user_id}"),
                    InlineKeyboardButton(f"close {emoji.WASTEBASKET}", f"close|{user_id}")
                ]
            ]
        ),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex(pattern=r"back"))
async def back_music_(client: Client, cb: CallbackQuery):
    bot_username = (await client.get_me()).username
    user_id = int(cb.data.split("|")[1])
    chat_id = cb.message.chat.id
    music = music_result[chat_id][0]
    k = 0
    res = "\n"
    for i in music:
        k += 1
        res += f"{k}. [{i['title'][:35]}...]({i['url']})\n"
        res += f"┣ {emoji.LIGHT_BULB} duration - {i['duration']}\n"
        res += f"┣ {emoji.FIRE} [More Information](https://t.me/{bot_username}?start=ytinfo_{i['url']})\n\n"

    temp = []
    keyboard = []
    inline_board = list(play_back_keyboard(user_id))
    for count, j in enumerate(inline_board, start=1):
        temp.append(j)
        if count % 3 == 0:
            keyboard.append(temp)
            temp = []
        if count == len(inline_board):
            keyboard.append(temp)
    await cb.edit_message_text(
        f"results\n{res}\n", reply_markup=InlineKeyboardMarkup(
            [
                keyboard[0],
                keyboard[1],
                [
                    InlineKeyboardButton(f"next {emoji.RIGHT_ARROW}", f"next|{user_id}"),
                    InlineKeyboardButton(f"close {emoji.WASTEBASKET}", f"close|{user_id}")
                ]
            ]
        )
    )
