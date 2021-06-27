import discord
from discord.ext import commands
from log import log
import asyncio
from random import randint
import Users
from abc import ABC, abstractmethod
import os

class NotMatchMaked(Exception):pass

class Game(ABC):
    game_timeout = 180

    @staticmethod
    def checkChannel(message, ctx, messageStrings=(), user=None):
        if user == None:
            messageUser = None
        else:
            messageUser = message.author
        if messageStrings != 0:
            return ctx.channel == message.channel and (message.content.strip() in messageStrings) and user == messageUser
        else:
            return ctx.channel == message.channel and messageUser == user

    @abstractmethod
    async def game(self, ctx):
        pass

    def __init__(self, client, minplayers, *, maxplayers=6):
        self.players = []
        self.gameStatus = False
        self.client = client
        self.maxplayers = maxplayers
        self.minplayers = minplayers

    async def matchmake(self, ctx):
        mmStarter = Users.Player(ctx.author)
        self.players.append(mmStarter)
        log(1, "starting matchmaking")
        await ctx.send("Started matchmaking on this channel. Type 'join' to join the game. ")
        def checkMM(message):
            return ctx.channel == message.channel #move to new global check
        while len(self.players) <= self.maxplayers:
            try:
                response = await self.client.wait_for('message', check=checkMM, timeout=self.game_timeout)
            except asyncio.TimeoutError:
                await ctx.send("Matchmaking cancelled due to inactivity.")
                self.players.clear()
                return False
            else:
                if response.content.startswith("join"):
                    if response.author not in list(map(lambda player: player.member, self.players)): #perf issues
                        if len(self.players) <= self.maxplayers:
                            self.players.append(Users.Player(response.author))
                            await ctx.send(f"Added {str(response.author)} to the list of players. There are currently {len(self.players)} out of {self.minplayers} **required** players. ")
                            if len(self.players) >= self.minplayers:
                                await ctx.send("The game currently has the minimum amount of players. The author can type 'start' to start the game. ")
                        else:
                            await ctx.send("Sorry, the game is currently full.")
                    else:
                        await ctx.send("You already joined the game.")
                elif response.content.startswith("start"):
                    if self.maxplayers >= len(self.players) >= self.minplayers:
                        if response.author == mmStarter.member:
                            return True
                        else:
                            await ctx.send(f"{response.author.mention}, only the game's matchmaker can start the game, who is {mmStarter.member.mention}")
                    else:
                        await ctx.send(f"There needs to be a minimum of {self.minplayers} players to start the game.")
                elif response.content.startswith("quit"):
                    activated = False
                    for i, player in enumerate(self.players):
                        if player.member == response.author:
                            self.players.pop(i)
                            activated = True
                            break
                    if activated:
                        await ctx.send(f"Removed {response.author.mention} from the list of players.")
                elif response.content.startswith("players"):
                    if response.author in list(map(lambda player: player.member, self.players)):
                        sendStr = ""
                        for player in self.players:
                            sendStr += str(player.member.mention)+", "
                        await ctx.send("**Current players - **\n"+sendStr[:-2])
                    else:
                        await ctx.send("Please join the game before viewing its queue. ")

    async def start(self, ctx):
        mmStatus = await self.matchmake(ctx)
        if mmStatus and self.maxplayers >= len(self.players) >= self.minplayers:
            await ctx.send(f"Starting game with {len(self.players)} players....")
            self.gameStatus = True
            await self.game(ctx)
        else:
            # raise NotMatchMaked("The game's player count does not fit in between the maximum and minimum player counts.")
            await ctx.send("The game's player count does not fit in between the maximum and minimum player counts.")

class RussianR(Game):
    def __init__(self, client):
        super().__init__(client, 2, maxplayers=6)
        self.bulletLocation = randint(0, 5)

    async def game(self, ctx):
        # --------- add lethal ------------
        for i in range(0, 5):
            playersIndex = i%len(self.players)
            await ctx.send(f"It's {self.players[playersIndex].getMention()} turn. Type 'shoot' to shoot. ")
            try:
                response = await self.client.wait_for('message', check=lambda message: self.checkChannel(message, ctx, "shoot"), timeout=self.game_timeout)
            except asyncio.TimeoutError:
                await ctx.send("Game cancelled due to inactivity.")
                return False
            else:
                await ctx.send("3")
                await asyncio.sleep(1)
                await ctx.send("2")
                await asyncio.sleep(1)
                await ctx.send("1")
                await asyncio.sleep(1)
                if i == self.bulletLocation:
                    await ctx.send(f"BAM!!! {self.players[playersIndex].getMention()} shot himself right in the head. All other players remain alive... until the next time...")
                    return True
                else:
                    await ctx.send("No bullet was shot. On to the next player!")

class TicTac(Game):
    def __init__(self, client):
        super().__init__(client, minplayers=2, maxplayers=2)

    @staticmethod
    async def printBoard(ctx, places, message=None):
        embed = discord.Embed()
        printStr = f'''
        {places[0][0]}  |  {places[0][1]}  |  {places[0][2]}
        ---------------
        {places[1][0]}  |  {places[1][1]}  |  {places[1][2]}
        ---------------
        {places[2][0]}  |  {places[2][1]}  |  {places[2][2]}
        '''
        embed.add_field(name="**Board**", value=printStr)
        if message is None:
            message = await ctx.send(embed=embed)
            return message
        else:
            await message.edit(embed=embed)

    async def checkBoard(self, acceptedReactions):
        for i, row in enumerate(acceptedReactions):
            if row[0] == row[1] == row[2]: #checking rows
                return True
            if acceptedReactions[0][i] == acceptedReactions[1][i] == acceptedReactions[2][i]: #checking columns
                return True
            if (acceptedReactions[0][0] == acceptedReactions[1][1] == acceptedReactions[2][2]) or (acceptedReactions[0][2] == acceptedReactions[1][1] == acceptedReactions[2][0]):
                return True


    async def game(self, ctx):
        async def updateMessage(message):
            nMessage = await ctx.fetch_message(message.id)
            return nMessage
        signs = ['❌', '⭕']
        acceptedReactions = [["1️⃣", "2️⃣", "3️⃣"], ["4️⃣", "5️⃣", "6️⃣"], ["7️⃣", "8️⃣", "9️⃣"]]
        board = await self.printBoard(ctx, acceptedReactions)
        for row in acceptedReactions:
            for reaction in row:
                await board.add_reaction(reaction)
        board = await updateMessage(board)
        await ctx.send("The board is ready. Click one of the reactions that corresponds with the place you want to pick.")
        def check(reaction, user, currMember):
            reactionAccepted = False
            for rrow in acceptedReactions:
                if reactionAccepted:
                    break
                for acceptedreaction in rrow:
                    if acceptedreaction == reaction.emoji:
                        reactionAccepted = True
                        break
            return reaction.message.id == board.id and reactionAccepted and user == currMember
        for i in range(0, 8):
            try:
                currMember = self.players[i%len(self.players)].member
                if 'turnMessage' in locals():
                    await turnMessage.edit(content=f"It's {currMember.mention}'s turn!")
                else:
                    turnMessage = await ctx.send(f"It's {currMember.mention}'s turn!")
                reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=lambda reaction, user: check(reaction, user, currMember))
            except TimeoutError:
                await ctx.send("Game closed due to inactivity.")
                return False
            else:
                found = False
                for k, row in enumerate(acceptedReactions): #finding the index of the reaction
                    if found:
                        break
                    for j, acceptedreaction in enumerate(row):
                        if str(reaction) == acceptedreaction:
                            acceptedReactions[k][j] = signs[i%2]
                            found = True
                            break
                board = await updateMessage(board) #not neccesary
                await board.clear_reaction(reaction.emoji)
                await self.printBoard(ctx, acceptedReactions, board)
                if await self.checkBoard(acceptedReactions):
                    await ctx.send(f"{user.mention} is the winner!")
                    return True
        await ctx.send("Unfortunately, no one won. Better luck next time!")

class Games(commands.Cog):
    games = {}

    def __init__(self, client):
        log(1, "Game cog loaded")
        # cfgPath = os.getenv("LOCALAPPDATA")+"\\DiscordBot\\games.json"
        # if not os.path.exists(cfgPath):
        #     file = open(cfgPath, 'w')
        self.client = client

    @commands.command()
    async def open(self, ctx, *args):
        if ctx.guild.id not in self.games.keys():
            try:
                gameType = args[0]
            except:
                await ctx.send("Specify a game type...")
            else:
                maxplayers = None
                try:
                    maxplayers = args[1]
                except:
                    pass
                finally:
                    if gameType.lower() == "russianr":
                        self.games[ctx.guild.id] = RussianR(self.client)
                        await self.games[ctx.guild.id].start(ctx)
                        self.games.pop(ctx.guild.id)
                    if gameType.lower() == "tictactoe":
                        if commands.has_permissions(manage_emojis=True):
                            self.games[ctx.guild.id] = TicTac(self.client)
                            await self.games[ctx.guild.id].start(ctx)
                            self.games.pop(ctx.guild.id)
                        else:
                            await ctx.send('The "Manage Emojis" permission is required to play this game. Please add it to my role and try again.')
                    else:
                        await ctx.send("You typed an incorrect type of game. Please choose between russianr or tictactoe.")
        else:
            await ctx.send("A game is currently in progress on this server. Please wait until it finishes before starting a new one.")