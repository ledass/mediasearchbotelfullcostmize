import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.WARNING)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyromod import listen
from pyrogram.idle import idle
from utils import Media
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL


class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        self.username = '@' + me.username
        print(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")

        # ✅ Send message to log channel
        if LOG_CHANNEL:
            try:
                await self.send_message(LOG_CHANNEL, f"✅ Bot started as {me.mention}")
            except Exception as e:
                print(f"❌ Cannot send message to log channel: {e}")

        # ✅ Keep the bot running
        await idle()

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")


app = Bot()
app.run()
🧪 Test Check Before Running
.env file must include:

ini
Copy code
LOG_CHANNEL=-100xxxxxxxxxx
Your info.py must include this:

python
Copy code
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL")) if os.environ.get("LOG_CHANNEL") else None
Your bot must be admin in the log channel.

Let me know if you'd like a .zip of this working setup or help testing on Koyeb or Replit.











Tools



ChatGPT can make mistakes. Check important info. See Cookie Preferences.


app = Bot()
app.run()
