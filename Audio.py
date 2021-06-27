from discord.ext import commands, tasks
import discord
import os
from log import log
import youtube_dl
from youtube_api import YoutubeDataApi
from html import unescape
import asyncio

CONFIG = {
        "VOLUME": 0.5,
        "DESCRIPTION_MAX": 100
}

class Song():
    def __init__(self, video, url, title, **kwargs):
        self.video = video
        self.url = url
        self.title = title
        self.description = kwargs["description"]
        self.date = kwargs["date"]
        self.channel = kwargs["channel"]
        self.image = kwargs["image"]
        self.duration = kwargs["duration"]
        self.views = kwargs["views"]

class Queue():
    def __init__(self, volume):
        self.songs = []
        self.volume = volume
        self.loop = False

    def getLength(self):
        totalLength = 0
        for song in self.songs:
            totalLength += song.duration
        return totalLength

    def addSong(self, song):
        self.songs.append(song)

class Audio(commands.Cog):
    queues = {}
    embedlinks = {}
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '96',
        }]
    }
    def __init__(self, client):
        log(1, "Audio cog loaded")
        # self.client.lavaClient = lavalink.Client(self.client.user.id)
        # self.client.lavaClient.add_node('localhost', 7000, 'ROGB', 'na', 'mNode')
        # self.client.add_listener(self.client.lavaClient.voice_update_handler, 'on_socket_response')
        # self.client.lavaClient.add_event_hook(self.track_hook)
        self.ytdata = YoutubeDataApi("AIzaSyBLFHcjVfzoIsjvwnO9qxby6MzLqdpZE9A")
        log(1, f"Audio Configuration: VOLUME {CONFIG['VOLUME']}      MAX-DESC {CONFIG['DESCRIPTION_MAX']}")
        self.client = client
    #     self.client.wavelink = wavelink.Client(bot=self.client)
    #     self.client.loop.create_task(self.start_nodes())
    #
    # async def start_nodes(self):
    #     await self.client.wait_until_ready()
    #
    #     # Initiate our nodes. For this example we will use one server.
    #     # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
    #     await self.client.wavelink.initiate_node(host='localhost',
    #                                           port=2333,
    #                                           rest_uri='http://0.0.0.0:2333',
    #                                           password='youshallnotpass',
    #                                           identifier='TEST',
    #                                           region='us_central')

    # async def track_hook(self, event):
    #     if isinstance(event, lavalink.events.QueueEndEvent):
    #         guild_id = int(event.player.guild_id)
    #         await self.connect_to(guild_id, None)

    #-----------------OLD COOLDOWN SYSTEM START-------------------------
    ####################################################################
    # async def playQueue(self, ctx, boundChannel): #start going through the queue
    #     FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', #fixes socket disconnects
    #                       'options': '-vn'}
    #     checkingChannel = True
    #
    #     def moveToNext():
    #         nonlocal checkingChannel
    #         checkingChannel = False
    #         nonlocal boundChannel
    #         try:
    #             if self.queues[ctx.guild.id].loop == False: #if no loop
    #                 self.queues[ctx.guild.id].songs.pop(0) #no song in queue
    #             else:
    #                 v = ctx.guild.voice_client.channel #checking every loop
    #                 if not len(v.voice_states) > 1:
    #                     self._stopVC(ctx)
    #         except: #empty queue
    #             try:
    #                 self.queues[ctx.guild.id] #see if a queue exists
    #             except:
    #                 pass
    #             else:
    #                 try:
    #                     while not len(self.queues[ctx.guild.id].songs) > 0:
    #                         v = ctx.guild.voice_client.channel
    #                         if v is None or ctx.guild.voice_client.channel.id != boundChannel:
    #                             break
    #                         # v = ctx.guild.voice_client.channel.id #check if needed
    #                         # v = self.client.get_channel(v) #check if needed
    #                         if not len(v.voice_states) > 1:
    #                             self._stopVC(ctx)
    #                         else:
    #                             asyncio.run(asyncio.sleep(5))
    #                 except:
    #                     pass
    #         else:
    #             if ctx.guild.voice_client is not None:
    #                 if len(self.queues[ctx.guild.id].songs) > 0: #if there is a song then play
    #                     if not self.queues[ctx.guild.id].loop:
    #                         self.client.loop.create_task(ctx.send(embed=discord.Embed(title=f':play_pause: Now playing - "{self.queues[ctx.guild.id].songs[0].title}"', color=discord.Colour.dark_red())))
    #                     volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
    #                     volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
    #                     ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())
    #                     checkingChannel = True
    #                     iter = 0
    #                     while checkingChannel:
    #                         if not len(ctx.guild.voice_client.channel.voice_states) > 1:
    #                             self._stopVC(ctx)
    #                         else:
    #                             iter = 0
    #                         if ctx.guild.voice_client.channel.id != boundChannel:
    #                             if len(ctx.guild.voice_client.channel.voice_states) > 1:
    #                                 asyncio.run((f"Somebody moved me to {ctx.guild.voice_client.channel}. Continuing to play...."))
    #                                 boundChannel = ctx.guild.voice_client.channel.id
    #                             else:
    #                                 asyncio.run(ctx.send(f"Somebody moved me to {ctx.guild.voice_client.channel}. Leaving the channel since there are no users in it..."))
    #                                 self._stopVC(ctx)
    #                                 checkingChannel = False
    #                         else:
    #                             asyncio.run(asyncio.sleep(2))
    #                         iter += 1
    #                 else: #if not
    #                     moveToNext()
    #             else:
    #                 self._stopVC(ctx)
    #     volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
    #     volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
    #     ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())
    #     iter = 0
    #     while checkingChannel:
    #         if iter == 10:
    #             if not len(ctx.guild.voice_client.channel.voice_states) > 1:
    #                 self._stopVC(ctx)
    #             else:
    #                 iter = 0
    #         if ctx.guild.voice_client.channel.id != boundChannel:
    #             if len(ctx.guild.voice_client.channel.voice_states) > 1:
    #                 await ctx.send(f"Somebody moved me to {ctx.guild.voice_client.channel}. Continuing to play....")
    #                 boundChannel = ctx.guild.voice_client.channel.id
    #             else:
    #                 await ctx.send(f"Somebody moved me to {ctx.guild.voice_client.channel}. Leaving the channel since there are no users in it...")
    #                 self._stopVC(ctx)
    #                 checkingChannel = False
    #         else:
    #             await asyncio.sleep(2)
    #         iter += 1

    async def playQueue(self, ctx, boundChannel): #start going through the queue
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', #fixes socket disconnects
                          'options': '-vn -af loudnorm=I=-16:LRA=11:TP=-1.5'}
        def moveToNext():
            try:
                if self.queues[ctx.guild.id].loop == False: #if no loop
                    self.queues[ctx.guild.id].songs.pop(0) #no song in queue
            except:pass #empty queue
            else:
                if ctx.guild.voice_client is not None:
                    if len(self.queues[ctx.guild.id].songs) > 0: #if there is a song then play
                        if not self.queues[ctx.guild.id].loop:
                            self.client.loop.create_task(ctx.send(embed=discord.Embed(title=f':play_pause: Now playing - "{self.queues[ctx.guild.id].songs[0].title}"', color=discord.Colour.dark_red())))
                        volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
                        volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
                        ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())
                    else: #if not
                        moveToNext()
                else:
                    self._stopVC(ctx)
        volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
        volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
        ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())

    @staticmethod
    def userVCState(ctx):
        return ctx.message.author.voice != None

    @commands.command()
    @commands.check(userVCState.__func__)
    async def pause(self, ctx):
        if await self.checkChannel(ctx):
            ctx.guild.voice_client.pause()

    @commands.command()
    @commands.check(userVCState.__func__)
    async def resume(self, ctx):
        if await self.checkChannel(ctx):
            ctx.guild.voice_client.resume()

    async def checkChannel(self, ctx):
        if ctx.guild.voice_client.channel != ctx.author.voice.channel:
            await ctx.send("You are not connected to the same channel as the bot.")
            return False
        else:
            return True

    async def checkQueue(self, ctx):
        try:
            self.queues[ctx.guild.id]
        except:
            await ctx.send("There is no queue. Check if the bot is connected to a channel.")
            return False
        else:
            if len(self.queues[ctx.guild.id].songs) > 0:
                return True
            else:
                await ctx.send("The queue is empty.")
                return False

    @commands.command()
    @commands.check(userVCState.__func__)
    async def loop(self, ctx):
        if await self.checkQueue(ctx) and await self.checkChannel(ctx):
            self.queues[ctx.guild.id].loop = True
            await ctx.send(f'Started looping "**{self.queues[ctx.guild.id].songs[0].title}**". To stop looping, type !stoploop or to skip the song, type !skip')

    @commands.command()
    @commands.check(userVCState.__func__)
    async def stoploop(self, ctx):
        if await self.checkQueue(ctx) and await self.checkChannel(ctx):
            if self.queues[ctx.guild.id].loop:
                self.queues[ctx.guild.id].loop = False
                await ctx.send(f'Stopped looping "**{self.queues[ctx.guild.id].songs[0].title}**"')
            else:
                await ctx.send("There is no song looping right now.")

    @commands.command()
    @commands.check(userVCState.__func__)
    async def skip(self, ctx):
        if await self.checkQueue(ctx) and await self.checkChannel(ctx):
            self.queues[ctx.guild.id].loop = False
            ctx.guild.voice_client.stop()
            await ctx.send(f':track_next: Skipped "{self.queues[ctx.guild.id].songs[0].title}"')

        # try:
        #     self.queues[ctx.guild.id]
        # except:
        #     await ctx.send("There is no queue. Check if the bot is connected to a channel.")
        #     return
        # if len(self.queues[ctx.guild.id].songs) > 0:
        #     ctx.guild.voice_client.stop()
        #     await ctx.send(f':track_next: Skipped "{self.queues[ctx.guild.id].songs[0].title}"')
        # else:
        #     await ctx.send("There is nothing to skip. The queue is empty.")

    @commands.command()
    @commands.check(userVCState.__func__)
    async def remove(self, ctx, num=None):
        if await self.checkChannel(ctx):
            if ctx.guild.id in self.queues and len(self.queues[ctx.guild.id].songs) > 1:
                try:
                    num = int(num)
                except:
                    await ctx.send("You typed an invalid number.")
                else:
                    if len(self.queues[ctx.guild.id].songs) >= num >= 1: #queue starts at number 1, not 0
                        await ctx.send(f':ok_hand: Removed "{self.queues[ctx.guild.id].songs[num].title}"')
                        self.queues[ctx.guild.id].songs.pop(num)
                    else:
                        if num == 0:
                            await ctx.send("If you meant to skip the song, use !skip. Otherwise, choose a number between 1 and the amount of songs.")
                        else:
                            await ctx.send(f"There are {len(self.queues[ctx.guild.id].songs)-1} songs in the queue, excluding the one currently playing. Please choose a number between 1 and {len(self.queues[ctx.guild.id].songs)-1}.")
            else:
                await ctx.send("There are no songs in the queue.")

    @commands.Cog.listener() #Voice_State listener
    async def on_voice_state_update(self, member, before, after): #Voice_State listener
        cGuild = self.client.get_guild(member.guild.id)
        vClient = cGuild.voice_client
        # if vClient and vClient.is_connected() and vClient.channel:
        #     if vClient.channel == before.channel:
        #         if len(vClient.channel.members) == 1:
        #             if vClient.is_playing() == True:
        #                 await asyncio.sleep(20)
        #             else:
        #                 await asyncio.sleep(5)
        #             if len(vClient.channel.members) == 1:
        #                 self._stopVC(cGuild)
        #     else:
        #         if len(vClient.channel.members) == 1:
        #             self._stopVC(cGuild)
        # elif self.queues.get(cGuild.id):
        #     if member.id == self.client.user.id: #uneccesary? unsure if unneccesary since there is no chance that the bot will be disconnected and at the same time have queue
        #         self._stopVC(cGuild)
        if member.id == self.client.user.id:
            if not before.channel == after.channel:
                if after.channel and before.channel:
                    if len(vClient.channel.members) == 1:
                        self._stopVC(cGuild)
                elif not after.channel and before.channel:
                    if self.queues.get(member.guild.id):
                        self._stopVC(cGuild)
        elif member.id != self.client.user.id and vClient and vClient.is_connected() and (before.channel == vClient.channel or after.channel == vClient.channel):
            if before.channel and before.channel == vClient.channel: #if user  our channel
                if len(vClient.channel.members) == 1:
                    if vClient.is_playing() == True:
                        await asyncio.sleep(45)
                    else:
                        await asyncio.sleep(20)
                    if len(vClient.channel.members) == 1:
                        self._stopVC(cGuild)


    def _stopVC(self, guild): #can either send guild or context
        if guild is discord.ext.commands.context: #if CONTEXT
            guild = guild.guild
        if guild.voice_client:
            try:
                self.client.loop.create_task(guild.voice_client.disconnect(force=True))
            except:
                pass
        try:
            self.queues.pop(guild.id)
        except:
            pass

    @commands.command(aliases=["disconnect", "stop", "die", "quit", "kys", "commit_sepuku", "kill_joseph"])
    @commands.check(userVCState.__func__)
    async def leave(self, ctx):
        if await self.checkChannel(ctx):
            cVoiceClient = ctx.guild.voice_client
            if cVoiceClient:
                await cVoiceClient.disconnect()
                self.queues.pop(ctx.guild.id)
            else:
                await ctx.send("The bot isn't currently in a voice channel.")

    @staticmethod
    async def getLength(duration):
        if int(duration/60) == 0:
            return f'{str(duration%60)+"s"}'
        else:
            return f'{str(int(duration/60))+"m"} {str(duration%60)+"s"}'

    async def getVideoEmbed(self, video, ctx):
        embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.red())
        try:
            if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
                totalLength = self.queues[ctx.guild.id].getLength()
                embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
        except:pass
        if not video.description == "" and len(video.description) > CONFIG["DESCRIPTION_MAX"]:
            description = unescape(video.description)[:CONFIG["DESCRIPTION_MAX"]] + "...."
        elif video.description == "":
            description = None
        else:
            description = unescape(video.description)
        embed.set_thumbnail(url=video.image)
        length = await self.getLength(video.duration)
        embed.add_field(name="Duration", value=length, inline=True)
        embed.add_field(name="Uploaded By", value=str(unescape(video.channel)), inline=True)
        embed.add_field(name="Views", value=video.views, inline=True)
        if description is not None:
            embed.add_field(name="Description", value=description, inline=True)
        return embed

    async def search(self, ctx, arg): #searches by string argument and returns a youtube link
        searchMessage = await ctx.send("**Searching...**")
        def checkResponse(message):
            return message.channel == ctx.channel and message.author == ctx.author
        search = self.ytdata.search(q=arg)
        await searchMessage.delete()
        if len(search) == 0:
            await ctx.send("No results were found. Try a different song name.")
            return -1
        sendStr = "**Choose Video** (type the video's number)\n"
        for i, video in enumerate(search):
            sendStr += f"{i + 1}. {unescape(video['video_title'])}\n"
        await ctx.send(sendStr)
        while(True):
            try:
                response = await self.client.wait_for('message', timeout=360, check=checkResponse)
            except:
                if ctx.guild.voice_client and not ctx.guild.voice_client.is_playing():
                    await ctx.guild.voice_client.disconnect()
                    self.queues.pop(ctx.guild.id)
                    return -1
            else:
                try:
                    response = int(response.content)
                except:
                    response = response.content.split(" ")[0]
                    if response.lower() == "!play" or response.lower() == "!p" or response.lower() == "!youtube": #check if there is already another search. if so then don't add
                        return -1
                    pass
                else:
                    if not ctx.guild.voice_client:
                        await ctx.send("The bot isn't connected to a voice channel anymore, and therefore your search selection could not be completed. Please search for the song again to make the bot join your channel.")
                        return -1
                    elif len(search) >= response >= 1:
                        return 'https://www.youtube.com/watch?v='+search[response - 1]["video_id"]
                    else:
                        await ctx.send("You typed an invalid selection. Search for the song again. ")
                        return -1

    @commands.command()
    async def ytinfo(self, ctx, *args):
        if "watch?v" not in args[0].lower():
            url = " ".join(args)
            search = await self.search(ctx, url)
        else:
            search = args[0]
        video = await self.createSong(search)
        embed = await self.getVideoEmbed(video, ctx)
        embed.set_footer(text="Just type !play (no name required) to play this song.")
        await ctx.send(embed=embed)
        self.embedlinks[ctx.guild.id] = search

    # async def createSong(self, url, info=None):
    #     if info is None:
    #         with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
    #             info = ydl.extract_info(url=url, download=False)
    #     song = Song(info['formats'][0]['url'], url, info['title'], description=info["description"], image=info["thumbnail"], views=info["view_count"], duration=info["duration"], date=info["upload_date"], channel=info["uploader"])
    #     return song

    async def createSong(self, url, info=None):
        loop = asyncio.get_event_loop()
        if info is None:
            result = await loop.run_in_executor(None, youtube_dl.YoutubeDL, self.ydl_opts)
            with result as ydl:
                try:
                    info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                except:
                    return -1
        song = Song(info['formats'][0]['url'], url, info['title'], description=info["description"], image=info["thumbnail"], views=info["view_count"], duration=info["duration"], date=info["upload_date"], channel=info["uploader"])
        return song

    @commands.command(aliases=["q", "next"])
    @commands.check(userVCState.__func__)
    async def queue(self, ctx):
        try:
            songs = self.queues[ctx.guild.id].songs
        except:
            await ctx.send("There is no queue. Check if the bot is connected to a channel.")
        else:
            if len(songs) > 0:
                fieldNames = list(map(lambda song: song.title, songs))
                if self.queues[ctx.guild.id].loop:
                    fieldNames[0] = '**[LOOP]** '+fieldNames[0]
                embed = discord.Embed(title="**Current Queue**")
                embed.set_footer(text=f"Estimated time for entire queue: {await self.getLength(self.queues[ctx.guild.id].getLength())}")
                embed.add_field(name="Currently Playing", value=fieldNames[0])
                def returnStr():
                    str = ""
                    for i, title in enumerate(fieldNames[1:]):
                        str += f"{i+1}. {title}\n"
                    return str
                if len(fieldNames) > 1:
                    embed.add_field(name="In Queue", value=returnStr(), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("The queue is currently empty.")

    @commands.command()
    @commands.check(userVCState.__func__)
    async def volume(self, ctx, volume):
        if await self.checkChannel(ctx):
            if not volume is None:
                try:
                    volume = float(volume)
                except:
                    await ctx.send("Invalid volume.")
                else:
                    if 0.1 <= volume <= 1:
                        self.queues[ctx.guild.id].volume = volume
                        await ctx.send(f"Volume changed to **{volume}**. The next songs in this session/queue will be played in the new volume, and will reset after the session ends. ")
                    else:
                        await ctx.send("Choose a volume between 0.1 and 1.")

    @commands.command(aliases=["p", "youtube", "music", "P", "PLAY", "soundcloud", "sc"])
    @commands.check(commands.has_permissions(manage_messages=True))
    async def play(self, ctx, *args):
        if len(args) > 0 or (ctx.guild.id in self.embedlinks.keys()):
            cVoiceClient = ctx.guild.voice_client
            if cVoiceClient and cVoiceClient.channel == ctx.message.author.voice.channel: # if connected to the right channel
                pass
            elif cVoiceClient:
                if cVoiceClient.is_playing():
                    await ctx.send("The bot is currently **playing a song** in another channel. Before joining a new channel, tell it to stop playing in the other channel by typing !leave. ")
                    return
                else:
                    await cVoiceClient.disconnect()
                    self.queues.pop(ctx.guild.id)
                    await ctx.message.author.voice.channel.connect()
            elif self.userVCState(ctx):
                await ctx.message.author.voice.channel.connect()
            else: 
                await ctx.send("You are not in a voice channel.")
                return
            data = None
            if(len(args) > 0):
                query = args[0].lower()
                if "watch?v" not in query and "soundcloud.com" not in query and "open.spotify.com" not in query:
                    url = " ".join(args)
                    search = await self.search(ctx, url)
                else:
                    search = args[0]
            else:
                search = self.embedlinks.pop(ctx.guild.id)
            if search != -1:
                if ctx.guild.voice_client.is_playing():
                    await ctx.send("**Adding to Queue**\n")
                else: #just checking whether the loop is still running (if more the one song then it must be running)
                    await ctx.send("**Now Playing**\n")
                if data is None:
                    song = await self.createSong(search)
                else:
                    song = await self.createSong(search, data)
                if song != -1:
                    embed = await self.getVideoEmbed(song, ctx)
                    await ctx.send(embed=embed)
                    if ctx.guild.id not in self.queues:
                        self.queues[ctx.guild.id] = Queue(CONFIG["VOLUME"])
                    self.queues[ctx.guild.id].addSong(song)
                    if not ctx.guild.voice_client.is_playing():
                        await self.playQueue(ctx, ctx.guild.voice_client.channel.id)
                else:
                    await ctx.send("Unable to fetch video. Are you sure the link you provided is valid?")

        else:
            await ctx.send("Please provide a YouTube search query or link to play.")