import configparser

import aiohttp
import discord
from discord.ext import commands, tasks

from hijri_calendar.hijri_calendar import HijriCalendar

config = configparser.ConfigParser()
config.read('config.ini')

# Takes token from IslamBot's config.ini.
token = config['IslamBot']['token']

description = "A Discord bot with Islamic utilities. View Qur'an, hadith, prayer times and more."

intents = discord.Intents(messages=True, guilds=True)


@tasks.loop(hours=1)
async def update_presence():
    hijri = HijriCalendar.get_current_hijri()
    game = discord.Game(f"/help | {hijri}")
    await bot.change_presence(activity=game)


@update_presence.before_loop
async def before_presence_update():
    await bot.wait_until_ready()


class IslamBot(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix='-', description=description, case_insensitive=True, intents=intents)
        self.initial_extensions = [
            "quran.quran",
            "quran.mushaf",
            "quran.morphology",
            "hijri_calendar.hijri_calendar",
            "salaah.salaah_times",
            "dua.dua",
            "hadith.hadith",
            "hadith.transmitter_biographies",
            "tafsir.arabic_tafsir",
            "tafsir.tafsir",
            "miscellaneous.reload",
            "miscellaneous.help",
            "miscellaneous.TopGG" # Remove if using the bot locally
        ]

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def on_ready(self):
        print(f'Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers')

        # Sync commands globally
        await bot.tree.sync(guild=None)

        # If you are using the bot locally, uncomment the below and comment out the statement above so that commands
        # only sync to your server. Global syncs are slow to propagate and are strictly rate-limited.
        # await bot.tree.sync(guild=discord.Object(308241121165967362))

        # Starting this in the setup hook causes a deadlock as before_presence_update calls wait_until_ready()
        update_presence.start()


bot = IslamBot()
bot.run(token)
