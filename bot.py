import discord
from discord.ext import commands, tasks
from discord import app_commands
from cogs.CoreCommands import CoreCommands
from cogs.Media import Media
from cogs.TextGames import TextGames
from databases.databases import Database

def run_discord_bot():
    # TOKEN
    with open("C:/Users/schwa/Desktop/TOKEN.txt", 'r') as token_file:
        TOKEN = token_file.read()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="*", intents=intents, case_insensitive=True)
    
    @bot.event
    async def on_ready():
        await bot.add_cog(CoreCommands(bot))
        await bot.add_cog(TextGames(bot))
        await bot.add_cog(Media(bot))
        print(f'{bot.user} is now running!')
        
        # sync commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        
        # store all user and server ID's in a database
        user_data = set()
        for guild in bot.guilds:
            for member in guild.members:
                user_data.add((str(guild.id), str(guild.name), str(member.id), str(member.name), str(member.avatar))) # add tuple containing data to set
        Database.store_servers_data(user_data)
        print("Database updated.")
        
    bot.run(TOKEN)