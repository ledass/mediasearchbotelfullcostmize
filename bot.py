import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.WARNING)

from pyrogram import Client, __version__, idle
from pyrogram.raw.all import layer
from pyromod import listen
from pyrogram import idle  # ✅ Correct import for Pyrogram v2
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
                await self.send_message(LOG_CHANNEL, "✅ Test log message")
            except Exception as e:
                print(f"❌ Failed to send to LOG_CHANNEL: {e}")

        # ✅ Keep the bot running
        await idle()
        

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")



app = Bot()
app.run()
