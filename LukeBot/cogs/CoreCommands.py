import asyncio
from bs4 import BeautifulSoup
import discord
from discord import Embed, app_commands
from discord.ext import commands
import random
import time
from datetime import datetime
import pytz
from databases.databases import Database
import httpx
from io import BytesIO
from PIL import Image

random.seed(time.time())

class CoreCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="hello", description="Hey there!")
    async def hello(self, ctx):
        """Hey there!"""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
            
        await ctx.send(f"Hey there, {ctx.author.mention}!")
        
    @commands.hybrid_command(name="wave", description="Wave to someone!")
    async def wave(self, ctx, user: discord.Member = None): # Kiss another member!
        """Wave to someone!"""
        if not user:
            await ctx.send("Correct usage: *wave @mention")
            return
        
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id), str(user.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id), str(user.id))
            

        await ctx.send(f"{ctx.author.mention} waves to {user.mention}!")
        await ctx.send("https://media1.tenor.com/m/Qy5sUxL5phgAAAAC/forest-gump-wave.gif")
        
    @commands.hybrid_command(name = "punch", description="Punch someone!")
    async def punch(self, ctx, user: discord.Member = None): # Punch another member!
        """Punch someone!"""
        if not user:
            await ctx.send("Correct usage: *punch @mention")
            return
        
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id), str(user.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id), str(user.id))
        
        await ctx.send(f"{ctx.author.mention} punches {user.mention}!")
        await ctx.send("https://media1.tenor.com/m/jwGSFHGRyFUAAAAC/boxing-tom-and-jerry.gif")
        
    @commands.hybrid_command(name="time", description="Get the time in U.S. time zones.")
    async def time(self, ctx):
        """Get the time in U.S. time zones."""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
        
        await ctx.send(f"PST: {datetime.now(pytz.timezone("America/Los_Angeles")).strftime("%Y-%m-%d %I:%M:%S %p")}\n"
                       f"MST: {datetime.now(pytz.timezone("America/Denver")).strftime("%Y-%m-%d %I:%M:%S %p")}\n"
                       f"CST: {datetime.now(pytz.timezone("America/Chicago")).strftime("%Y-%m-%d %I:%M:%S %p")}\n"
                       f"EST: {datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d %I:%M:%S %p")}\n")
        
    @commands.hybrid_command(name="rtd", description="Roll the dice.")
    async def rtd(self, ctx):
        """Roll the dice."""    
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
        
        await ctx.send(file=discord.File(f'assets/dice/DIE_0{random.randint(1,6)}.png'))

    @commands.hybrid_command(name="avatar", description="Change the bot avatar")
    async def avatar(self, ctx, img: str = None):
        """Change the bot avatar. Can use saved avatars, URL, or img file"""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id), img)
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id), img)
        
        
        def is_valid_img(response: httpx.Response) -> bool:
            """Reads in binary data, returns true or false determined by pillow's supported file types"""
            try:
                test_image_type = Image.open(BytesIO(response.content))
            except:
                return False
            
            return True
        
        def url_to_imgfile(response: httpx.Response, num: int):
            """Grabs image data and writes it to file with unique name"""
            image_data = response.content
            file = open(f"assets/avatars/{num}.png", 'wb')
            file.write(image_data)
            file.close()
        
        set_avatar = ""
        use_stored_avatar = False
        response = None
        avatar_filepath = None
        
        # user sends img attachment or doesn't add anything
        if img is None: 
            try:        
                # if user sends attachment, discord will automatically create a URL for that attachment.
                set_avatar = str(ctx.message.attachments[0])
                response = httpx.get(set_avatar)
            except:
                await ctx.send("Please send a form of image content when calling the command. Attachment, name of a stored avatar, or an image URL.")
                return
            
        # from database, numbers 1 to length of stored images table
        elif img.isdigit(): 
            if int(img) in Database.get_ids("avatars"):
               use_stored_avatar = True
               avatar_filepath = f'assets/avatars/{img}.png'
            else:
                await ctx.send("If attempting to use existing avatar, please try again and enter correct number of the avatar you are attempting to use.")
                return
        
        # check for valid img url
        else: 
            try:
                response = httpx.get(img)
                set_avatar = img
            except:
                await ctx.send("URL could not be reached. Please enter valid argument for image - existing image ID (*al), image URL, or image attatchment.")
                return

        # after grabbing url from any source, check if it is valid image.
        if (not is_valid_img(response)) and (not use_stored_avatar):
            await ctx.send("Image is not valid. Filetype not supported, or URL is  not directly to an image. Process aborted.")
            return

        # user enters url that already exists in database
        elif Database.check_existing_avatar_url(set_avatar):
            await ctx.send("Avatar URL already exists. Updating avatar...")
            
        # Only prompt IF user enters new URL for avatar
        elif not use_stored_avatar: 
            await ctx.send("Please uniquely name the avatar:")
            try:
                user_message = await self.bot.wait_for("message", check= lambda mess: mess.author == ctx.author, timeout = 30)
            except asyncio.TimeoutError:
                await ctx.send("Name not entered in time, aborting process.")
                return
            
            # store new avatar information and create image file
            avatar_name = str(user_message.content)
            Database.store_avatar_data(set_avatar, avatar_name, str(user_message.author.id))
            url_to_imgfile(response, Database.get_largest_rowid("avatars"))
        
        # find image file in database from associated URL or ID, then upload image as avatar
        # if user is using stored avatar, then avatar filepath is already valid.
        # should probably just get avatar ID as string and append '.png' instead, since filename derives from id
        if not use_stored_avatar:
            avatar_filepath = Database.get_avatar_file_path(set_avatar)[0]
            
        with open(avatar_filepath, 'rb') as image:
            await self.bot.user.edit(avatar=image.read())
            await ctx.send("Avatar updated successfully.")
        
    @commands.hybrid_command(name="al", description="List of all stored bot avatars")
    async def avatar_list(self, ctx):
        """View all LukeBot saved avatars!"""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
        
        avatar_embed = discord.Embed(title="Avatar List", description="To set LukeBot's avatar with an image from this list, use *al 'id number'")
        for avatar_data in Database.get_table("avatars"):
            
            try:
                username = (await self.bot.fetch_user(int(avatar_data[4]))).name
            except:
                username = "User Not Found"

            avatar_embed.add_field(name=f"ID: {avatar_data[0]}", value=f"Name: {avatar_data[3]}, Added by: {username}", inline=False)
        
        await ctx.send(embed=avatar_embed)
        
async def setup(bot):
    await bot.add_cog(CoreCommands(bot))