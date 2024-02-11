import info
from utils.broadcast.access import db
from pyrogram import Client
from pyrogram.types import Message


async def AddUserToDatabase(bot: Client, cmd: Message):
    if not await db.is_user_exist(cmd.from_user.id):
        await db.add_user(cmd.from_user.id)
