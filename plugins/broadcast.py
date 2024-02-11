import time
import string
import random
import asyncio
import datetime
import traceback
import aiofiles.os
import info
from utils.broadcast.access import db
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
)
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)

broadcast_ids = {}


@Client.on_message(
    filters.private
    & filters.command("broadcast")
    & filters.user(info.ADMINS)
    & filters.reply
)
async def _broadcast(_, bot: Message):
    await broadcast_handler(bot)


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        logger.warning("Floodwait occured while broadcast, sleeping for %s sec", e.value)
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


async def broadcast_handler(m: Message):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = "".join(
            [random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text="Broadcast Started! You will be notified with log file when complete"
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users, current=done, failed=failed, success=success
    )
    async with aiofiles.open("broadcast.txt", "w") as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user["id"]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user["id"])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(current=done, failed=failed, success=success)
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}.\n{success} success and {failed} failed.",
            quote=True,
        )
    else:
        await m.reply_document(
            document="broadcast.txt",
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}.\n{success} success and {failed} failed.",
            quote=True,
        )
    await aiofiles.os.remove("broadcast.txt")


@Client.on_message(
    filters.private
    & filters.command("stats")
    & filters.user(info.ADMINS)
)
async def stats(bot, m: Message):
    all_users = await db.get_all_users()
    out = await m.reply_text(
        text="Status check started! You will be notified when complete"
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    failed = 0
    success = 0
    async for user in all_users:
        name = bool()
        try:
            name = await bot.send_chat_action(int(user["id"]), enums.ChatAction.TYPING)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        if bool(name):
            success += 1
        else:
            failed += 1
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await m.reply_text(
        text=f"Status check completed in `{completed_in}`\n\nTotal users {total_users}.\n{success} active\n{failed} blocked or deleted.",
        quote=True,
    )
    await out.delete()
