import bot
import discord
from discord import app_commands
from discord.ext import commands
import random
import time
import asyncio
import os
import httpx
import json
from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageFilter
from io import BytesIO
from databases.databases import Database

class TextGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="typerace", description="Create a type racer lobby.")
    async def type_race(self, ctx):
        """Create a TypeRacer lobby."""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
        
        await ctx.send(f"Please type 'race' to join/leave race. {ctx.author.mention} may begin the race by typing 'start' or cancel by typing 'cancel'")
        racing_users = {ctx.author} # set of users currently ready to race
        
        # pre-race 'lobby'
        while(True):
            user_message = await self.bot.wait_for("message")
            user_message_content = str(user_message.content)
            
            if user_message_content == "race": # user types race
                if user_message.author in racing_users and not ctx.author: # if user is not author and has already entered race, he now exits race.
                    await ctx.send(f"User {bot.user_message.author} removed from race.")
                    racing_users.remove(user_message.author)

                elif user_message.author != ctx.author: # if user is not author and types race
                    await ctx.send(f"User {user_message.author.mention} added to race.")
                    racing_users.add(user_message.author)
            
            if user_message_content == "cancel": # if typerace initiator types *cancel, race is canceled. return to end function
                await ctx.send("Race Cancelled.")
                return
                
            if user_message_content == "start" and user_message.author == ctx.author: # typerace initiator types *start, race begins
                break
        
        # grab typing prompt
        with open("assets/typing_prompts.txt", "r") as typing_file:
            typing_prompt = typing_prompt = random.choice(typing_file.readlines()).rstrip("\n")

        for i in range(5, 0, -1): #Countdown
            if i == 5:
                await ctx.send("Prompt in 5...")
            else:
                await ctx.send(str(i) + "...")
            time.sleep(1)
            
        await ctx.send(typing_prompt)
        
        init_time = time.time() # Time race started
        user_data = dict() # will hold users and wpm once race is finished
        one_warning = False # ensures users get ONE 10 second warning rather than multiple spam messages, as bot.wait_for updates multiple times per second
        
        while(time.time() < init_time + 45 and len(racing_users) != 0):
            stopwatch = time.time()
            try:
                user_message = await self.bot.wait_for("message", check = lambda mess: mess.author in racing_users, timeout = 0.5)
            except asyncio.TimeoutError:
                user_message = None
                print("this is a test")
                print(time.time())
            
            if user_message:
                user_message_content = str(user_message.content)
            
            if user_message_content == "end": # end race early
                await ctx.send(f"{user_message.author.mention} has ended the race early.")
                break
            
            if user_message_content == typing_prompt: # user types prompt correctly
                await ctx.send(f"{user_message.author.mention} has finished!")
                user_data[user_message.author] = ((len(typing_prompt)/5)/((time.time() - init_time)/60.0)) # user : wpm
                racing_users.remove(user_message.author) # remove user from set
                
            elif not user_message:
                pass
            
            elif user_message_content != typing_prompt: # user types prompt incorrectly
                await ctx.send(f"Wrong, {user_message.author.mention}, try again!")
            
            if (init_time + 45 - stopwatch < 11 and init_time + 45 - stopwatch > 9 and not one_warning): # 10 second warning
                one_warning = True
                await ctx.send("10 seconds left...")
            

        await ctx.send("\nRace Over! Results:")
        time.sleep(1)
        
        # Placements
        for i, user in enumerate(user_data): 
            await ctx.send(f"{i + 1}. {user.mention}: {int(user_data[user])} WPM")
        if len(racing_users) != 0:
               for user in racing_users:
                   await ctx.send(f"{user.mention} did not finish.")
                   
    @commands.hybrid_command(name="wordle",description="Create a wordle game.")
    async def wordle(self, ctx): 
        """Create a wordle game."""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id))
        
        def create_grid(guesses: list[str]=None, word: str='') -> discord.File: # creates and fills grid based on list of user guesses
            if guesses is None:
                guesses = []
                
            grid = Image.new('RGB', (500,600), color=(207, 207, 207)) # create image background
            text_plane = ImageDraw.Draw(grid) # plane for characters to be drawn on
            font = ImageFont.truetype("arial.ttf", 60)
            for i in range(len(guesses)): # six rows
                if guesses[i]: # if not empty
                    temp_word = word # keeps track of correctly guessed/yellow letters so that there cannot be more yellows than there are instanes of that char
                    
                    #green letters
                    for j, char in enumerate(guesses[i]): 
                        if char == word[j]: # correct char = green
                            temp_word = temp_word.replace(char, '', 1)
                            grid.paste(Image.open('assets/wordle/GreenSquare.png'), (j*100, i*100))
                            text_plane.text((j*100 + 25, i*100 + 25), str(char).upper(), (0,0,0), font=font)
                    
                    #yellow letters
                    for j, char in enumerate(guesses[i]): 
                        if char in temp_word and char != word[j]: # incorrect but in word = yellow
                            temp_word = temp_word.replace(char, '', 1)
                            grid.paste(Image.open('assets/wordle/YellowSquare.png'), (j*100, i*100))
                            text_plane.text((j*100 + 25, i*100 + 25), str(char).upper(), (0,0,0), font=font)
                            
                        #if green/yellow exhausted of that char, should be gray
                        elif char in word and char != word[j] and char not in temp_word: 
                            grid.paste(Image.open('assets/wordle/ColorAbsent.png'), (j*100, i*100))
                            text_plane.text((j*100 + 25, i*100 + 25), str(char).upper(), (0,0,0), font=font)
                    
                    # final gray letters
                    for j, char in enumerate(guesses[i]):
                        if char not in word:    
                            grid.paste(Image.open('assets/wordle/ColorAbsent.png'), (j*100, i*100))
                            text_plane.text((j*100 + 25, i*100 + 25), str(char).upper(), (0,0,0), font=font)
                
            grid.save('assets/wordle/grid.png')
            grid.close()
            return discord.File("assets/wordle/grid.png")

        # Set up initial embed below
        wordle_embed = discord.Embed(title="WORDLE", description="Type any five-letter word to guess!")
        grid_file = create_grid() # create empty grid to start
        wordle_embed.set_image(url="attachment://grid.png")
        
        update = await ctx.send(embed=wordle_embed, file=grid_file) #store embed message to update embed later
        
        # load dict of words
        try: 
            word_site = "https://gist.githubusercontent.com/scholtes/94f3c0303ba6a7768b47583aff36654d/raw/d9cddf5e16140df9e14f19c2de76a0ef36fd2748/wordle-La.txt"
            response = httpx.get(word_site) 
            if response.status_code == 200:
                WORDS = response.content.splitlines()
        except:
            await ctx.send("Word site failed to load")
            return

        idx = random.randint(0, len(WORDS) - 1)

        rand_words = [] # will get answer word as well as 6 words in case user does not enter word within time limit


        # Keep looping until 7 words (one for answer, 6 for auto-guesses)
        while len(rand_words) < 7:  
            idx = random.randint(0, len(WORDS) - 1)
            word = WORDS[idx].decode("ascii")
            if word not in rand_words:
                rand_words.append(word)
        

        ans_word = random.choice(list(rand_words)) # 5-letter 'answer' word
        rand_words.remove(ans_word) # remove answer from random words
        
        #print(ans_word) 
        
        guess_list = [] # list of guesses

        flag_guess = False # flag for correct user guess
        
        for i in range(1,7): # loop through six guesses
            flag_time = False # time limit flag
            
            try:
                user_guess = await self.bot.wait_for("message", timeout=120.0, check = lambda mess: mess.author == ctx.author and len(mess.content) == 5)
            except asyncio.TimeoutError:
                await ctx.send(f"Time limit for guess exceeded! Random word {rand_words[0]} guessed.")
                flag_time = True

            guess = str(user_guess.content).lower() # always should be lowercase
            if flag_time == False: # add user guess if user guesses in time
                guess_list.append(guess)
            else:
                guess_list.append(rand_words[0]) # if time limit exceeded, add from randWord
                rand_words.remove(rand_words[0])
                
            grid_file = create_grid(guess_list, ans_word)
            await update.edit(embed=wordle_embed, attachments=[grid_file]) # update embed (grid image has changed)
            if guess == ans_word: # WIN CASE
                await ctx.send(f"Congratulations! {ctx.author.mention} won wordle! The word was: {ans_word}. Guesses taken: {len(guess_list)}")
                flag_guess = True
                break
            
        if flag_guess == False:
            await ctx.send(f"{ctx.author.mention} has failed wordle. The word was: {ans_word}")
        
        os.remove('assets/wordle/grid.png') # delete generated grid image
                

    @commands.hybrid_command(name="picdle", description="Guess the animal!")
    async def picdle(self, ctx, difficulty: str = None):
        """Guess cat or dog. Easy, Med, or Hard"""
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id), difficulty)
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id), difficulty)
            
        if not difficulty:
            await ctx.send("Please try again and enter a difficulty. see *help for options.")
            return
        
        # Image from URL into bytes to send in discord embed (tested here using a different method, not downloading images)
        def url_to_imgfile(response: httpx.Response, embed: discord.Embed, blur: int = None) -> discord.File:
                image_data = BytesIO(response.content)
                image = Image.open(image_data)
                if blur != None:
                    image = image.filter(ImageFilter.BoxBlur(blur))
                image_data = BytesIO()  # Create a new BytesIO object for saving the image
                image.save(image_data, format='PNG')
                image_data.seek(0)
                file_image = discord.File(image_data, filename="image.png")
                embed.set_image(url="attachment://image.png")
                return file_image
        
        animal_options = {0: "dog", 1: "cat"}
        difficulties_blur = {"easy": 10, "med": 20, "hard": 40}
        update = None
        first_send = True
        time_flag = False
        
        try:
            selected_difficulty = difficulties_blur[difficulty.lower()]
        except:
            await ctx.send(f"Difficulty {difficulty} not valid.")
            return
        
        while(True):
            coinflip = random.randint(0,1)
            if coinflip == 0: # dog
                response = httpx.get("https://dog.ceo/api/breeds/image/random")
                image_url = response.json().get("message")
                response = httpx.get(image_url)
            elif coinflip == 1:
                response = httpx.get("https://cataas.com/cat")
            
            if response.status_code == 200:
                animal_embed = discord.Embed(title="Cat or Dog?", description="To guess, type 'cat' or 'dog'. 'end' will end the game.")
    
                file_image = url_to_imgfile(response, animal_embed, selected_difficulty)
                
                if first_send == True:
                    update = await ctx.send(embed=animal_embed, file=file_image)
                    first_send = False
                else:
                    await update.edit(embed=animal_embed, attachments=[file_image])

                # reload image and make it unblurred. this does not update it yet, we will that later after user input
                file_image = url_to_imgfile(response, animal_embed)
                
            else:
                await ctx.send("Image not fetched")
                break
            
            # User guess
            try:
                user_guess = await self.bot.wait_for("message", timeout=30.0, check = lambda mess: mess.author == ctx.author and (mess.content == 'cat' or mess.content.lower() == 'dog'or mess.content.lower() == 'end'))
            except asyncio.TimeoutError: # if time out, show unblurred image and end game
                await ctx.send(f"Time limit for guess exceeded! Answer was: {animal_options[coinflip]}")
                await update.edit(embed=animal_embed, attachments=[file_image])
                return

            await update.edit(embed=animal_embed, attachments=[file_image]) # update discord embed with unblurred image

            # user correct guess
            if str(user_guess.content).lower() == animal_options[coinflip]: 
                await update.add_reaction("✅")
                await asyncio.sleep(1)
                await update.remove_reaction(emoji="✅", member=self.bot.user)
            
            # user ends game
            elif str(user_guess.content).lower() == 'end': 
                await ctx.send(f"Game ended. Answer was: {animal_options[coinflip]}")
                return
            
            # user wrong guess
            else: 
                await ctx.send(f"Wrong! Answer was: {animal_options[coinflip]}. Game Over!")
                return

    @commands.hybrid_command(name="ttt", description="challenge another user to tic-tac-toe")
    async def ttt(self, ctx, user: discord.Member = None):
        """ Challenge another user to Tic-Tac-Toe"""
        if not user:
            await ctx.send("Correct usage: *ttt @mention")
            return
        
        if ctx.guild:
            Database.cmd_to_db(ctx.command.name, str(ctx.guild.id), str(ctx.author.id), str(user.id))
        else:
            Database.cmd_to_db(ctx.command.name, "DM", str(ctx.author.id), str(user.id))
        
        # function creates and fills grid based on list of user placement
        def add_turn(first_start: bool, place: int=None, letter: chr=None) -> discord.File: 
            if first_start == True:
                grid = Image.open('assets/tictactoe/grid.png') # create image background
            else:
                grid = Image.open('assets/tictactoe/gridNEW.png')
            match place:
                case 1:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (0,0))
                case 2:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (167,0))
                case 3:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (334,0))
                case 4:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (0,167))
                case 5:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (167,167))
                case 6:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (334,167))
                case 7:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (0,334))
                case 8:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (167,334))
                case 9:
                    grid.paste(Image.open(f'assets/tictactoe/{letter}.png'), (334,334))
                case _:
                    pass
            grid.save('assets/tictactoe/gridNEW.png')
            grid.close()
            return discord.File("assets/tictactoe/gridNEW.png")
        
        # discord user accept/deny challenge
        await ctx.send(f"{user.mention}: You have 10 seconds to accept or deny {ctx.author.mention}'s TIC-TAC-TOE challenge. 'accept' or 'deny'.")
        try:
            user_ans = await self.bot.wait_for("message", check = lambda mess: mess.author == user and (mess.content.lower() == 'accept' or mess.content.lower() == 'deny'), timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.send(f"Game cancelled. {user.mention} failed to respond.")
            return
        if str(user_ans.content) == 'deny':
            await ctx.send(f"{user.mention} denied TIC-TAC-TOE.")
            return
        await ctx.send(f"Game starting! {ctx.author.mention} has first move.")
        
        user_placed = {
            1: None, 2: None, 3: None, 
            4: None, 5: None, 6: None, 
            7: None, 8: None, 9: None
            }
        
        win_combinations = [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [1, 5, 9],
          [3, 5, 7],
          [1, 4, 7],
          [2, 5, 8],
          [3, 6, 9]
        ]
        
        # set up initial embed
        ttt_embed = discord.Embed(title="TIC-TAC-TOE", description="Type desired grid number for your turn.")
        empty_grid = add_turn(True) # pass no args except bool to create new empty grid
        ttt_embed.set_image(url='attachments://gridNEW.png')
        update = await ctx.send(embed=ttt_embed, file=empty_grid)
        
        # flag for win con
        flag = False
        
        for i in range(9):
            user_num = None # for scope
            # user enters 1-9 to make their turn.
            try:
                if i % 2 == 0:
                    msg = await self.bot.wait_for("message", check = lambda mess: mess.author == ctx.author and (int(mess.content) < 10 and int(mess.content) > 0 and user_placed[int(mess.content)] is None), timeout=15.0)
                    user_num = int(msg.content)
                    user_placed[user_num] = 'x'
                else:
                    msg = await self.bot.wait_for("message", check = lambda mess: mess.author == user and (int(mess.content) < 10 and int(mess.content) > 0 and user_placed[int(mess.content)] is None), timeout=15.0)
                    user_num = int(msg.content)
                    user_placed[user_num] = 'o'
            except asyncio.TimeoutError:
                await ctx.send("User failed to respond in time. Game forfeited.")
                break
                
            # update grid
            grid_file = add_turn(False, user_num, user_placed[user_num])
            await update.edit(embed=ttt_embed, attachments=[grid_file])
            
            # check for win
            if i > 3: # no need to check unless 3 x's minimum have been placed
                for win in win_combinations:
                    if user_placed[win[0]] == 'x' and user_placed[win[1]] == 'x' and user_placed[win[2]] == 'x':
                        await ctx.send(f"TIC-TAC-TOE!: User {ctx.author.mention} has won!")
                        flag = True
                        break
                    elif user_placed[win[0]] == 'o' and user_placed[win[1]] == 'o' and user_placed[win[2]] == 'o':
                        await ctx.send(f"TIC-TAC-TOE!: User {ctx.author.mention} has won!")
                        flag = True
                        break
                    
            # if win is true break
            if flag == True:
                break
        
        # if loop has passed and no win condition has been met, no winner (cat's game)
        if flag == False:
            await ctx.send("Cat's game!")
        
        # remove generated png file
        os.remove('assets/tictactoe/gridNEW.png')
            
    '''
    @commands.hybrid_command(name='ub', description='Ultimate Bravery.')
    async def ultimateBravery(self, ctx):
        return
    '''    

async def setup(bot):
    await bot.add_cog(TextGames(bot))