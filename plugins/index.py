import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserIsBlocked
from pyromod.exceptions.listener_timeout import ListenerTimeout
from pyromod.exceptions.listener_stopped import ListenerStopped
from pyromod.helpers import ikb

from info import ADMINS

from utils import save_file
logger = logging.getLogger(__name__)
lock = asyncio.Lock()

can_kb = ikb([[("❌ Cancel", "cancel_s")]])


@Client.on_message(filters.command(['index', 'indexfiles']) & filters.user(ADMINS))
async def index_files(bot, message):
    """Save channel or group files"""
    user_id = message.from_user.id
    if lock.locked():
        await message.reply('Wait until previous process complete.')
    else:
        while True:
            try:
                last_msg = await bot.ask(text="Forward me last message of a channel which I should save to my database.\n\nYou can forward posts from any public channel, but for private channels bot should be an admin in the channel.\n\nMake sure to forward with quotes (Not as a copy)", chat_id=message.from_user.id, reply_markup=can_kb, timeout=1800)
            except ListenerTimeout:
                try:
                    await bot.send_message(
                        user_id, "Request timed out, you can try again with /index"
                    )
                    return
                except UserIsBlocked:
                    return
            except ListenerStopped:
                return
            try:
                last_msg_id = last_msg.forward_from_message_id
                if last_msg.forward_from_chat.username:
                    chat_id = last_msg.forward_from_chat.username
                else:
                    chat_id = last_msg.forward_from_chat.id
                await bot.get_messages(chat_id, last_msg_id)
                break
            except Exception as e:
                await last_msg.reply_text(f"This Is An Invalid Message, Either the channel is private and bot is not an admin in the forwarded chat, or you forwarded message as copy.\nError caused Due to <code>{e}</code>")
                continue

        msg = await message.reply('Processing...⏳')
        total_files = 0
        async with lock:
            try:
                total = last_msg_id + 1
                current = int(os.environ.get("SKIP", 2))
                nyav = 0
                while True:
                    try:
                        message = await bot.get_messages(chat_id=chat_id, message_ids=current, replies=0)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        message = await bot.get_messages(
                            chat_id,
                            current,
                            replies=0
                        )
                    except Exception as e:
                        print(e)
                        pass
                    try:
                        for file_type in ("document", "video", "audio"):
                            media = getattr(message, file_type, None)
                            if media is not None:
                                break
                            else:
                                continue
                        media.file_type = file_type
                        media.caption = message.caption
                        await save_file(media)
                        total_files += 1
                    except Exception as e:
                        print(e)
                        pass
                    current += 1
                    nyav += 1
                    if nyav == 20:
                        await msg.edit(f"Total messages fetched: {current}\nTotal messages saved: {total_files}")
                        nyav -= 20
                    if current == total:
                        break
                    else:
                        continue
            except Exception as e:
                logger.exception(e)
                await msg.edit(f'Error: {e}')
            else:
                await msg.edit(f'Total {total_files} Saved To DataBase!')
