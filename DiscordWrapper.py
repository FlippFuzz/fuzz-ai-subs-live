import asyncio
import threading

import yt_dlp
from discord.ext.commands import Bot, Context

import credentials
from asyncio import run_coroutine_threadsafe
from discord import TextChannel, Intents, Interaction

from Settings import Settings


# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://discord.com/api/oauth2/authorize?client_id=1116722298934796418&permissions=3072&scope=bot
class DiscordWrapper:
    channel_name_must_contain = "NOT+SET+YET"
    channels: list[TextChannel] = []

    def __init__(self, settings: Settings):
        intents = Intents.default()
        intents.message_content = True
        self.bot = Bot(command_prefix="!", intents=intents)
        self.settings = settings

        @self.bot.check
        async def is_correct_channel(interaction: Interaction) -> bool:
            return self.channel_name_must_contain in interaction.channel.name

        @self.bot.hybrid_command()
        async def restart(ctx: Context):
            """
            Restart and update self

            Parameters
            ----------
            ctx

            Returns
            -------
            """
            self.settings.must_restart = True
            self.settings.must_exit = True

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
                              f"Translating: {self.settings.title}\n" \
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
        async def prompt(ctx: Context, enabled: bool):
            """
            Enable or disable prompt for translation/transcription
            Details about prompts can be found at:
            https://platform.openai.com/docs/guides/speech-to-text/prompting

            Parameters
            ----------
            enabled:
                yes or no
            ctx: Context

            Returns
            -------
            """
            self.settings.prompt_enabled = enabled
            await ctx.send(f"Updated Settings:\n{self.settings}.")

        @settings_group.command()
        async def translate(ctx: Context, enabled: bool):
            """
            Enable or disable translation

            Parameters
            ----------
            enabled:
                yes or no
            ctx: Context

            Returns
            -------
            """
            self.settings.translate = enabled
            await ctx.send(f"Updated Settings:\n{self.settings}.")

        @settings_group.command()
        async def buffer_time(ctx: Context, time: int):
            """
            Amount of the video to buffer before translating.
            This will restart the translation, causing an extra delay of buffer_time

            Parameters
            ----------
            time:
                Integer >= 1. Example: 10
            ctx: Context

            Returns
            -------
            """
            if time >= 1:
                self.settings.buffer_time_seconds = time
                settings.must_restart = True
                await ctx.send(f"Updated Settings:\n{self.settings}.")
            else:
                await ctx.send(f"\"{time}\" is invalid. Needs to be >= 1.")

        @self.bot.event
        async def on_ready():
            print(f"Discord bot logged in as: {self.bot.user.name}, {self.bot.user.id}")
            self.channel_name_must_contain = self.bot.user.name.rsplit("-")[-1]
            print(f"Channel Name Must Contain: {self.channel_name_must_contain}")

            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if self.channel_name_must_contain in channel.name:
                        self.channels.append(channel)
                        print(f"Will send messages to {channel.guild.name} - {channel}")

                self.send_message(f"Bot has started and is waiting for commands. Version: {self.settings.version}")

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
