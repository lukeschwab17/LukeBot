from databases.databases import Database
import discord
import asyncio


# store all user and server ID's in a database
async def store_guilds(bot):
    user_data = set()
    for guild in bot.guilds:
        for member in guild.members:
            user_data.add(
                (
                    str(guild.id),
                    str(guild.name),
                    str(member.id),
                    str(member.name),
                    str(member.avatar),
                )
            )  # add tuple containing data to set
    Database.store_servers_data(user_data)
    print("Database updated.")
    await asyncio.sleep(0)
