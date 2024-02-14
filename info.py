import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
USER_SESSION = environ.get('USER_SESSION', 'User_Bot')
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']
USERBOT_STRING_SESSION = environ.get('USERBOT_STRING_SESSION')

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ['ADMINS'].split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ['CHANNELS'].split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', None)
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else auth_channel
AUTH_CHANNEL_LINK = environ.get('AUTH_CHANNEL_LINK', None)

# MongoDB information
DATABASE_URI = environ['DATABASE_URI']
DATABASE_NAME = environ['DATABASE_NAME']
BROADCAST_DB_NAME = environ.get('BROADCAST_DB_NAME', "msb_broadcast_db")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'msb_files')

# Messages
default_start_msg = """
**Hi, I'm Media Search bot**

Here you can search files in here or inline mode. Just send the search query to get files
"""
default_help_msg = """
**Hi, I'm Media Search bot**
Use me to find files you required, just send a keyword & the bot will send the file if it is available.
"""

START_MSG = environ.get('START_MSG', default_start_msg)
HELP_MSG = environ.get('HELP_MSG', default_help_msg)
SHARE_BUTTON_TEXT = 'Checkout {username} for searching files'
INVITE_MSG = environ.get('INVITE_MSG', f'Please join [channel]({AUTH_CHANNEL_LINK}) to use this bot')
CUSTOM_FILE_CAPTION = environ.get('CUSTOM_FILE_CAPTION', None)
AUTO_DELETE_DELAY = int(environ.get('AUTO_DELETE_DELAY', 0))
