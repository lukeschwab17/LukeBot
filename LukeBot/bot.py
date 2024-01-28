import discord
from discord.ext import commands, tasks
from discord import app_commands
from cogs.CoreCommands import CoreCommands
from cogs.Media import Media
from cogs.TextGames import TextGames
from databases.databases import Database
from file_paths import BOT_TOKEN
from guild_data import store_guilds


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="*", intents=intents, case_insensitive=True)

    @bot.before_invoke
    async def before_command(ctx):
        await store_guilds(bot)

    @bot.event
    async def on_ready():
        await bot.add_cog(CoreCommands(bot))
        await bot.add_cog(TextGames(bot))
        await bot.add_cog(Media(bot))
        print(f"{bot.user} is now running!")

        # sync commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

        store_guilds(bot)

    bot.run(BOT_TOKEN)
