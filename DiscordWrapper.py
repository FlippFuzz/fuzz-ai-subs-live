import asyncio
import threading

import yt_dlp
from discord.ext.commands import Bot

import credentials
from asyncio import run_coroutine_threadsafe
from discord import TextChannel, Intents, Client


# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://discord.com/api/oauth2/authorize?client_id=1116722298934796418&permissions=3072&scope=bot
class DiscordWrapper:
    ALLOWED_CHANNEL_NAMES = {"ai-sub"}
    channels: list[TextChannel] = []
    video_m3u8 = ""

    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        self.bot = Bot(command_prefix="!", intents=intents)

        @self.bot.command()
        async def translate(ctx, url):
            message = f"ERROR: Cannot locate M3U8 for {url}"
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                if "formats" in info and len(info["formats"]) > 0:
                    self.video_m3u8 = info["formats"][0]['url']
                    title = info['title']
                    message = f"Command accepted. Will take around 30-60s before first TL is shown.\n"
                    message += f"Title: {title}\nM3U8: {self.video_m3u8}"

            await ctx.send(message)

        @self.bot.event
        async def on_ready():
            print("Discord bot logged in as: %s, %s" % (self.bot.user.name, self.bot.user.id))
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if channel.name in self.ALLOWED_CHANNEL_NAMES:
                        self.channels.append(channel)
                        print(f"Will send messages to {channel.guild.name} - {channel}")

                self.send_message("Bot has started and is waiting for commands")

        self.loop = asyncio.get_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever)

        self.loop.create_task(self.bot.start(credentials.discord_api_key))
        self.thread.start()

    async def __terminate_discord_client(self):
        await self.bot.close()
        self.loop.stop()

    def terminate_discord_client(self):
        run_coroutine_threadsafe(self.__terminate_discord_client(), self.loop)

    async def __send_message(self, msg: str):
        for channel in self.channels:
            await channel.send(msg)

    def send_message(self, msg: str):
        run_coroutine_threadsafe(self.__send_message(msg), self.loop)
