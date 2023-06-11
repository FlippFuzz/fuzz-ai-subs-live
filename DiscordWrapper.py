import asyncio
import threading

import yt_dlp
from discord.ext.commands import Bot, Context

import credentials
from asyncio import run_coroutine_threadsafe
from discord import TextChannel, Intents

from Settings import Settings


# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://discord.com/api/oauth2/authorize?client_id=1116722298934796418&permissions=3072&scope=bot
class DiscordWrapper:
    ALLOWED_CHANNEL_NAMES = {"ai-sub"}
    channels: list[TextChannel] = []

    def __init__(self, settings: Settings):
        intents = Intents.default()
        intents.message_content = True
        self.bot = Bot(command_prefix="!", intents=intents)
        self.settings = settings

        @self.bot.hybrid_command()
        async def translate(ctx: Context, url: str):
            """
            Select a video to translate
            
            Parameters
            ----------
            url: str
                URL to translate.
                Example: https://youtu.be/r-g0L9avCaE
            ctx: Context

            Returns
            -------
            """

            message = f"ERROR: Cannot locate M3U8 for {url}"
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                if "formats" in info and len(info["formats"]) > 0:
                    self.settings.video_m3u8 = info["formats"][0]['url']
                    self.settings.title = info['title']
                    self.settings.channel = info['channel']
                    message = f"Command accepted.\n" \
                              f"Settings: {self.settings}"
                    settings.must_restart = True

            await ctx.send(message)

        @self.bot.hybrid_group(name="settings")
        async def settings_group(ctx: Context):
            if ctx.invoked_subcommand is None:
                await ctx.send(f"{ctx.invoked_subcommand} is an invalid subcommand.")

        @settings_group.command()
        async def vad(ctx: Context, enabled: bool):
            """
            Enable or disable Voice Activity Detection(VAD) for translation

            Parameters
            ----------
            enabled:
                yes or no
            ctx: Context

            Returns
            -------
            """
            self.settings.vad_enabled = enabled
            await ctx.send(f"Updated Settings:\n{self.settings}.")

        @settings_group.command()
        async def buffer_time(ctx: Context, buffer_time: int):
            """
            Amount of the video to buffer before translating.
            This will restart the translation, causing an extra delay of buffer_time

            Parameters
            ----------
            buffer_time:
                Integer. Example: 10
            ctx: Context

            Returns
            -------
            """
            self.settings.segment_time_seconds = buffer_time
            settings.must_restart = True
            await ctx.send(f"Updated Settings:\n{self.settings}.")

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
