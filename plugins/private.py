import logging
from urllib.parse import quote
import re
import asyncio
from pyrogram import Client, emoji, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode

from utils import get_filter_results, get_file_details
from info import (
    CACHE_TIME,
    SHARE_BUTTON_TEXT,
    AUTH_USERS,
    AUTH_CHANNEL,
    CUSTOM_FILE_CAPTION,
    AUTO_DELETE_DELAY,
    AUTH_CHANNEL_LINK
)

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

BUTTONS = {}
BOT = {}


@Client.on_message(
    filters.text & filters.private & filters.incoming & filters.user(
        AUTH_USERS)
    if AUTH_USERS
    else filters.text & filters.private & filters.incoming
)
async def filter(client, message):
    if message.text.startswith("/"):
        return
    if AUTH_CHANNEL and AUTH_CHANNEL_LINK:
        try:
            user = await client.get_chat_member(int(AUTH_CHANNEL), message.from_user.id)
            if user.status == "kicked":
                await client.send_message(
                    chat_id=message.from_user.id,
                    text="Sorry Sir, You are Banned to use me.",
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
                return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.from_user.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🤖 Join Updates Channel", url=AUTH_CHANNEL_LINK
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        except Exception as e:
            logger.warning(e)
            await client.send_message(
                chat_id=message.from_user.id,
                text="Something went Wrong.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
    elif AUTH_CHANNEL and not AUTH_CHANNEL_LINK:
        logger.error("AUTH_CHANNEL_LINK missing")
        await client.send_message(
            chat_id=message.from_user.id,
            text="Something went Wrong.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif AUTH_CHANNEL_LINK and not AUTH_CHANNEL:
        logger.error("AUTH_CHANNEL missing")
        await client.send_message(
            chat_id=message.from_user.id,
            text="Something went Wrong.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 1 < len(message.text) < 100:
        btn = []
        search = message.text
        files = await get_filter_results(query=search)
        if files:
            for file in files:
                file_id = file.file_id
                filename = f"[{get_size(file.file_size)}] {file.file_name}"
                btn.append(
                    [
                        InlineKeyboardButton(
                            text=f"{filename}", callback_data=f"file_#{file_id}"
                        )
                    ]
                )
        else:
            await client.send_message(
                chat_id=message.from_user.id,
                text="No results found.\nOr retry with the correct spelling 🤐",
                reply_to_message_id=message.id,
            )
            return

        if not btn:
            return

        if len(btn) > 10:
            btns = list(split_list(btn, 10))
            keyword = f"{message.chat.id}-{message.id}"
            BUTTONS[keyword] = {"total": len(btns), "buttons": btns}
        else:
            buttons = btn
            buttons.append(
                [InlineKeyboardButton(text="📜 Pages 1/1",
                                      callback_data="pages")]
            )
            await message.reply_text(
                f"<b>Here is What I Found In My Database For Your Query {search} ‌‌‌‌‎ ­  ­  ­  ­  ­  </b>",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return

        data = BUTTONS[keyword]
        buttons = data["buttons"][0].copy()

        buttons.append(
            [InlineKeyboardButton(
                text="NEXT »»", callback_data=f"next_0_{keyword}")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📃 Pages 1/{data['total']}", callback_data="pages"
                )
            ]
        )
        await message.reply_text(
            f"<b>Here is What I Found In My Database For Your Query {search} ‌‌‌‌‎ ­  ­  ­  ­  ­  </b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


def size_formatter(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i: i + n]


async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if not user.status == "kicked":
            return True

    return False


def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    clicked = query.from_user.id
    try:
        typed = query.message.reply_to_message.from_user.id
    except Exception:
        typed = query.from_user.id
        pass
    if clicked == typed:

        if query.data.startswith("next"):
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer(
                    "You are using this for one of my old message, please send the request again.",
                    show_alert=True,
                )
                return

            if int(index) == int(data["total"]) - 2:
                buttons = data["buttons"][int(index) + 1].copy()

                buttons.append(
                    [
                        InlineKeyboardButton(
                            "«« BACK", callback_data=f"back_{int(index)+1}_{keyword}"
                        )
                    ]
                )
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📜 Pages {int(index)+2}/{data['total']}",
                            callback_data="pages",
                        )
                    ]
                )

                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            else:
                buttons = data["buttons"][int(index) + 1].copy()

                buttons.append(
                    [
                        InlineKeyboardButton(
                            "«« BACK", callback_data=f"back_{int(index)+1}_{keyword}"
                        ),
                        InlineKeyboardButton(
                            "NEXT ⏩", callback_data=f"next_{int(index)+1}_{keyword}"
                        ),
                    ]
                )
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📜 Pages {int(index)+2}/{data['total']}",
                            callback_data="pages",
                        )
                    ]
                )

                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return

        elif query.data.startswith("back"):
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer(
                    "You are using this for one of my old message, please send the request again.",
                    show_alert=True,
                )
                return

            if int(index) == 1:
                buttons = data["buttons"][int(index) - 1].copy()

                buttons.append(
                    [
                        InlineKeyboardButton(
                            "NEXT »»", callback_data=f"next_{int(index)-1}_{keyword}"
                        )
                    ]
                )
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📜 Pages {int(index)}/{data['total']}",
                            callback_data="pages",
                        )
                    ]
                )

                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            else:
                buttons = data["buttons"][int(index) - 1].copy()

                buttons.append(
                    [
                        InlineKeyboardButton(
                            "«« BACK", callback_data=f"back_{int(index)-1}_{keyword}"
                        ),
                        InlineKeyboardButton(
                            "NEXT ⏩", callback_data=f"next_{int(index)-1}_{keyword}"
                        ),
                    ]
                )
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📃 Pages {int(index)}/{data['total']}",
                            callback_data="pages",
                        )
                    ]
                )

                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
        elif query.data == "about":
            buttons = [
                [
                    InlineKeyboardButton(
                        "Update Channel", url="https://t.me/ELUpdates"
                    ),
                ]
            ]
            await query.message.edit(
                text="<b>Developer : <a href='https://t.me/CoderEL'>Coder EL</a>\nLanguage : <code>Python3</code>\nLibrary : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio</a>\n Update Channel : <a href='https://t.me/ELUpdates'>EL Updates</a> </b>",
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True,
            )

        elif query.data.startswith("file_"):
            ident, file_id = query.data.split("#")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name
                size = files.file_size
                f_caption = files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name=title, file_size=size, file_caption=f_caption
                        )
                    except Exception as e:
                        print(e)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
                buttons = [
                    [
                        InlineKeyboardButton(
                            "📥 More Bots 📥", url="https://t.me/ELUpdates/8"
                        ),
                    ]
                ]

                await query.answer()
                msg = await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                )
                if AUTO_DELETE_DELAY:
                    delay = AUTO_DELETE_DELAY/60 if AUTO_DELETE_DELAY > 60 else AUTO_DELETE_DELAY
                    delay = round(delay, 2)
                    minsec = str(
                        delay) + " mins" if AUTO_DELETE_DELAY > 60 else str(delay) + " secs"
                    disc = await client.send_message(
                        query.from_user.id,
                        f"Please save the file to your saved messages, it will be deleted in {minsec}",
                    )
                    await asyncio.sleep(AUTO_DELETE_DELAY)
                    await disc.delete()
                    await msg.delete()
                    await client.send_message(
                        query.from_user.id, "File has been deleted to avoid copyright"
                    )
        elif query.data.startswith("checksub"):
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(
                    "I Like Your Smartness, But Don't Be Oversmart 😒", show_alert=True
                )
                return
            ident, file_id = query.data.split("#")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name
                size = files.file_size
                f_caption = files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name=title, file_size=size, file_caption=f_caption
                        )
                    except Exception as e:
                        print(e)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                buttons = [
                    [
                        InlineKeyboardButton(
                            "📥 More Bots 📥", url="https://t.me/ELUpdates/8"
                        ),
                    ]
                ]

                await query.answer()
                msg = await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,

                )
                if AUTO_DELETE_DELAY:
                    delay = AUTO_DELETE_DELAY/60 if AUTO_DELETE_DELAY > 60 else AUTO_DELETE_DELAY
                    delay = round(delay, 2)
                    minsec = str(
                        delay) + " mins" if AUTO_DELETE_DELAY > 60 else str(delay) + " secs"
                    disc = await client.send_message(
                        query.from_user.id,
                        f"Please save the file to your saved messages, it will be deleted in {minsec}",
                    )
                    await asyncio.sleep(AUTO_DELETE_DELAY)
                    await disc.delete()
                    await msg.delete()
                    await client.send_message(
                        query.from_user.id, "File has been deleted to avoid copyright"
                    )
        elif query.data == "pages":
            await query.answer()
    else:
        await query.answer(
            "Nice.. Next Time Sure You Will Get It 🤭😝", show_alert=True
        )
