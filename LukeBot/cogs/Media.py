import asyncio
import random
from re import A
import time
import json
import httpx
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from discord import app_commands
from databases.databases import Database
from moviepy.editor import VideoFileClip, concatenate_videoclips
import shutil
import os
from PIL import Image
from pkg_resources import parse_version
from all_keys import TENOR_API_KEY

if parse_version(Image.__version__)>=parse_version('10.0.0'): # for pillow resizing to work
    Image.ANTIALIAS=Image.LANCZOS

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_recording_session = {}
        self.temp_videos_index = 0
        
    @commands.hybrid_command(name="gif", description="Receive a random gif based on the prompt.")
    async def gif(self, ctx, search: str):
        """Receive a random gif based on the prompt"""
        Database.cmd_to_db(ctx.command.name, "DM" if not ctx.guild else str(ctx.guild.id), str(ctx.author.id), search)
        
        search = search.replace(' ', '-') # spaces become %20 in image search. ############### LATER SHOULD IMPLEMENT MORE SUCH AS '+' ##############
        gif_links = []
        
        # grabbing gifs
        response = httpx.get(f"https://tenor.googleapis.com/v2/search?q={search}&key={TENOR_API_KEY}&limit={50}") #load first 500 gifs (timeout saved slow loading?)
        if response.status_code == 200:
            top100gifs = json.loads(response.content)
        else:
            await ctx.send("Error retrieving GIFs")
            return
            
        url = top100gifs['results'][random.randint(0, (len(top100gifs['results'])-1))]['url']
        
        await ctx.send(url)
 
    @commands.hybrid_command(name="wr", description="Retrieve information about LoL players or champions.")
    async def wr(self, ctx, search: str = None):
        """Retrieve information about LoL players or champions."""
        if not search:
            await ctx.send(r"Correct usage: \*wr 'player_username#id'  OR  \*wr 'champion_name'") # use raw string because discord uses * to format text
            return

        Database.cmd_to_db(ctx.command.name, "DM" if not ctx.guild else str(ctx.guild.id), str(ctx.author.id), search)
        
        new_arg = search.replace(' ', '') #spaces on u.gg website are removed

        headers = { # spoofing browser to webscrape
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.google.com/'
                }
        
        ### USER SEARCHES FOR PLAYER with '#' character ###
        if '#' in new_arg:
            new_arg = new_arg.replace('#', '-') # '#' changed to '-' in u.gg links
            response = httpx.get(f"https://u.gg/lol/profile/na1/{new_arg}/overview", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            try: # grab player data
                rank_img = soup.find("img", class_="rank-img")["src"]
                player_rank = soup.find(class_="rank-text").get_text(separator=' ', strip=True)
                player_info_container = soup.find(class_="rank-wins")
                player_wr_text = player_info_container.get_text(separator=' ', strip=True)
                player_games = player_info_container.find(class_="total-games")
                player_champs = soup.find_all(class_="champion-name") 
            except:
                await ctx.send("Player not found or is unranked this season.")
                return
            

            # formatting champion list
            player_champs_text = ""
            for i, champ in enumerate(player_champs): # playerChamps is ResultSet of champion text, make one string for dictionary value
                if i != (len(player_champs) - 1):
                    player_champs_text += (champ.text + ", ")
                else:
                    player_champs_text += champ.text

            # full player information
            player_info = {"Summoner Rank:": player_rank, "Summoner Winrate:": player_wr_text, "Summoner Champions:": player_champs_text}

            # create embed for player
            player_embed = discord.Embed(title=search.split("#", 1)[0].upper())
            for i, key in enumerate(player_info):
                if i == 2:
                    player_embed.add_field(name=key, value=player_info[key], inline=False)
                else:
                    player_embed.add_field(name=key, value=player_info[key])
            player_embed.set_thumbnail(url=rank_img)
            
            await ctx.send(embed=player_embed)
            
        ### USER SEARCHES FOR CHAMP ###
        else:
        #content of search URL
            response = httpx.get(f"https://u.gg/lol/champions/{new_arg}/build", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            try: # grab champ data
                champ_img = soup.find("img", class_="champion-image")["src"]
                champ_stats = soup.find(class_="additional-stats-container") # container that holds champion stats
                stats_values = champ_stats.find_all(class_="value") # values of champion stats
            except:
                await ctx.send("Champion Not Found.")
                return
        
            # create embed for champion
            champ_embed = discord.Embed(title=search.upper(), description="Champion Statistics")
            champInfo = {"Tier": stats_values[0].text, "Win Rate": stats_values[1].text, "Pick Rate": stats_values[2].text, "Ban Rate:": stats_values[3].text, "Matches": stats_values[4].text}
            for key in champInfo:
                champ_embed.add_field(name=key, value=champInfo[key])
            champ_embed.set_thumbnail(url=champ_img)

            await ctx.send(embed=champ_embed)
        

    @commands.hybrid_command(name="record_session", description="Gathers and compile clips while running")
    async def record_session(self, ctx):
        """Gathers and compiles clips into one while running. 'END RECORDING' to stop."""
        ### ADD TO DATABASE ###
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            await ctx.send("record_session command can only be used in a server.")
            return
        
        text_channel_id = ctx.channel.id

        def check_channel_and_content(message: discord.Message):
            # first, check if message is in the correct channel
            if message.channel != ctx.channel:
                return False
            # second, check if there is one or more attachments
            elif len(message.attachments) < 1:
                return False
            
            # not all attachments may be videos, so we need to grab only the ones that are.
            video_attachments = []
            for attachment in message.attachments:
                if attachment.content_type.startswith("video"):
                    video_attachments.append(str(attachment))
                    
            # if there is one or more video attachments, check passes
            if len(video_attachments) > 0:
                return True
            
            return False
             
        # Check if recording session is already in progress for this text channel
        if self.is_recording_session.get(text_channel_id, False):
            await ctx.send("Recording session is already in progress for this text channel.")
            return
        

        try:
            self.temp_videos_index += 1
            self.is_recording_session[text_channel_id] = True
            await ctx.send("Recording session begun! Clips sent in this text channel will be recorded. 'END RECORDING' to stop recording.")
            all_recordings = []
            user_ids = set()
            all_recording_filepaths = []
            # need to create temporary video file. because temporary files are written num.mp4, 
            # if multiple instances run, files will get overritten and deleted unless we create new directory for each function call
            temp_folder = f'assets/recording_sessions/{self.temp_videos_index}'
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            while True:
                # get videos continuously, stop when 2 hours of no uploads or END RECORDING entered.
                try:
                    get_video = await self.bot.wait_for("message", check=lambda mess: check_channel_and_content(mess) or str(mess.content) == "END RECORDING", timeout = 7200.0)
                    
                    if str(get_video.content) == "END RECORDING":
                        await ctx.send(f"{get_video.author.mention} has ended the recording session.")
                        break
                    
                    await ctx.send("Adding videos... Reminder: 'END RECORDING' to end the recording session!")
                    
                    for attachment in get_video.attachments:
                        if attachment.size > 25000000: # 25 mb size cap
                            await ctx.send(f"attachment: {attachment.url} not added. Size limit per attachment is 25 MB.")
                        else:
                            all_recordings.append(attachment)
                            user_ids.add(str(get_video.author.id))

                except asyncio.TimeoutError:
                    await ctx.send("No submissions for 2 hours. Recording completed.")
                    break
                
            if len(all_recordings) < 1: # if no video submissions, end before compiling video
                await ctx.send("Not enough recordings, video will not be made.")
                # delete temp folder
                try:
                    shutil.rmtree(temp_folder)
                    print("Directory removed successfully.")
                except OSError as e:
                    print(f"Error: {e}")
                return
            
            # saving files
            for i, recording in enumerate(all_recordings): 
                filename = i + 1
                try:
                    await recording.save(fp=f"{temp_folder}/{filename}.mp4")
                    all_recording_filepaths.append(f"{temp_folder}/{filename}.mp4")
                except:
                    await ctx.send(f"downloading clip {filename} failed.")
                    
                print("file saved")
                
            # https://thepythoncode.com/article/concatenate-video-files-in-python
            def concatenate(video_clip_paths: str, output_path: str, method="compose"):
                """Concatenates several video files into one video file
                and save it to `output_path`. Note that extension (mp4, etc.) must be added to `output_path`
                `method` can be either 'compose' or 'reduce':
                `reduce`: Reduce the quality of the video to the lowest quality on the list of `video_clip_paths`.
                `compose`: type help(concatenate_videoclips) for the info"""
                # create VideoFileClip object for each video file
                clips = [VideoFileClip(c) for c in video_clip_paths]
                if method == "reduce":
                    # calculate minimum width & height across all clips
                    min_height = min([c.h for c in clips])
                    min_width = min([c.w for c in clips])
                    # resize the videos to the minimum
                    clips = [c.resize((min_width, min_height)) for c in clips]
                    # concatenate the final video
                    final_clip = concatenate_videoclips(clips)
                elif method == "compose":
                    # concatenate the final video with the compose method provided by moviepy
                    final_clip = concatenate_videoclips(clips, method="compose")
                # write the output video file
                final_clip.write_videofile(output_path, audio_codec='aac')
                

            await ctx.send(f"OKAY {get_video.author.mention}, YOU HAVE 5 MINUTES TO ENTER NAME FOR RECORDING. IF YOU DON'T ENTER ONE, IT WILL NOT BE SAVED.")
            
            try:
                user_message = await self.bot.wait_for("message", check=lambda mess: mess.channel == ctx.channel and mess.author == get_video.author, timeout = 300.0)
            except asyncio.TimeoutError:
                await ctx.send("NO NAME ENTERED. PROCESS ABORTED.")
                

            await ctx.send(f"Compiling videos. This will take a while....")
            # compile videos and create video
            try:
                file_name = Database.get_largest_rowid("recording_session_compilations") + 1
                # if doesn't throw exception
                concatenate(all_recording_filepaths, rf"C:\Users\schwa\Desktop\video_website\video_website\video_website\static\videos\{file_name}.mp4", "reduce")
            except: # if does, it's the first of the table.
                concatenate(all_recording_filepaths, rf"C:\Users\schwa\Desktop\video_website\video_website\video_website\static\videos\{1}.mp4", "reduce")
                
            Database.submit_video(user_ids, len(all_recordings), str(user_message.content), str(ctx.guild.id))
            await ctx.send("Recordings compiled and saved.")
        
            # remove temp folder
            try:
                shutil.rmtree(temp_folder)
                print("Directory removed successfully.")
            except OSError as e:
                print(f"Error: {e}")
                
            # get video information from database
            video_info = Database.get_last_item("recording_session_compilations")
            print(video_info)
            
        finally:
            # reset the recording session status
            self.is_recording_session[text_channel_id] = False

    @commands.hybrid_command(name="videos", description="Website containing saved videos!")
    async def video_website(self, ctx):
        """View all LukeBot saved videos!"""
        Database.cmd_to_db(ctx.command.name, "DM" if not ctx.guild else str(ctx.guild.id), str(ctx.author.id))
        
        with open(r"C:\Users\schwa\Desktop\video_website\video_website\video_website\ngrok_url.json", "r") as file:
            ngrokdata = json.load(file)
            
        await ctx.send(f"Website containing saved compilations: {ngrokdata["tunnels"][0]["public_url"]}")
        
async def setup(bot):
    await bot.add_cog(Media(bot))