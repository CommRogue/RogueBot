from discord.ext import commands, tasks
import discord
from log import log
import youtubesearchpython as yt
from html import unescape
from sclib import SoundcloudAPI, Track
import asyncio
import wavelink
import StY
import utils
from urllib import parse

CONFIG = {
    "VOLUME": 0.5,
    "DESCRIPTION_MAX": 100
}


class invalidTypeError(Exception): pass


class invalidTrackTypeError(Exception): pass


class Playlist():
    def __init__(self, data, url):
        self.url = url
        self.cPosition = -1
        self.wavelinkTracks = None
        self.data = data
        self.video = None #current song

    async def next(self):
        return await self.goToSong(self.cPosition + 2)

    async def goToSong(self, number):
        if 0 < number <= len(self.wavelinkTracks):
             self.cPosition = number - 1
             self.video = self.wavelinkTracks[self.cPosition]
             return self.video
        else:
             return None

    def getLength(self):
        length = 0
        for i in range(self.cPosition, len(self.wavelinkTracks)-1):
            length += self.wavelinkTracks[i].length
        return length

class YTPlaylist(Playlist):
    def __init__(self, data, songs, url):
        super().__init__(data, url)
        self.wavelinkTracks = songs.tracks
        self.title = data["title"]
        self.image = data["thumbnails"]['thumbnails'][0]["url"]
        self.videoCount = data["videoCount"]
        self.channelName = data["channel"]["name"]
        self.channelLink = data["channel"]["link"]

class SCPlaylist(Playlist):
    def __init__(self, songs, url):
        super().__init__(None, url)
        self.wavelinkTracks = songs.tracks
        self.videoCount = len(songs.data['tracks'])
        self.title = songs.data['playlistInfo']['name']

class Song():
    def __init__(self, track, url):
        self.video = track
        self.url = url

class SpotifyPlaylist(Playlist):
    def __init__(self, songs, url, playlist, client):
        super().__init__(None, url)
        self.client = client
        self.tracks = songs
        self.videoCount = len(songs)
        self.data = playlist
        self.title = playlist['name']
        self.image = playlist['images'][0]['url']
        if "followers" in playlist:
            self.followers = playlist['followers']['total']
        if "popularity" in playlist:
            self.popularity = playlist['popularity']

    async def next(self):
        return await self.goToSong(self.cPosition + 2)

    async def goToSong(self, number):
        if 0 < number <= len(self.tracks):
            self.cPosition = number - 1
            video = self.tracks[self.cPosition]
            if video['wlTrack'] != None:
                self.video = video['wlTrack']
            else:
                v = await self.client.wavelink.get_tracks(f"ytsearch:{video['spTrack']['name']} {video['spTrack']['artists'][0]['name']}")
                video['wlTrack'] = v[0]
            self.video = video['wlTrack']
            return video['wlTrack']
        else:
            return None

    def getLength(self):
        length = 0
        for i in range(self.cPosition, len(self.tracks)-1):
            length += self.tracks[i]['spTrack']['duration_ms']
        return length

class SpotifySong(Song):
    def __init__(self, track, spotifyURL, spotifyInfo):
        super().__init__(track, spotifyURL)
        self.title = unescape(spotifyInfo['name'])
        if "album" in spotifyInfo:
            self.date = spotifyInfo["album"]['release_date']
            self.image = spotifyInfo["album"]["images"][0]["url"]
        else:
            self.date = spotifyInfo['release_date']
            self.image = spotifyInfo["images"][0]["url"]
        artistsStr = ""
        for artist in spotifyInfo["artists"]:
            artistsStr += f"[{artist['name']}]({artist['external_urls']['spotify']}), "
        self.artistStr = artistsStr[:-2]
        self.popularity = spotifyInfo["popularity"]
        if "duration_ms" in spotifyInfo:
            self.duration = round(spotifyInfo["duration_ms"]/1000)
        else:
            self.duration = round(spotifyInfo['tracks']['items'][0]["duration_ms"]/1000)

class YTSong(Song):
    def __init__(self, track, url, video):
        super().__init__(track, url)
        self.title = unescape(video['title'])
        if 'descriptionSnippet' in video and video['descriptionSnippet'] is not None:
            self.description = ''.join(list(map(lambda description: description['text'], video['descriptionSnippet'])))
        else:
            self.description = None
        #####Date not needed, it was causing problems with KeyError anyway
        # if video.get("publishedTime"):
        #     self.date = video["publishedTime"]
        # elif video.get("publishDate"):
        #     self.date = video["publishDate"]
        # else:
        #     self.date = None
        self.channelName = video["channel"]['name']
        self.channelLink = video["channel"]['link']
        self.image = video['thumbnails'][0]['url']
        if video.get("duration"):
            self.duration = video["duration"]
        self.views = video['viewCount']['short']


class SCSong(Song):
    def __init__(self, track, url):
        super().__init__(track, url)
        info = self.video.info
        self.title = unescape(info["title"])
        self.author = info["author"]
        self.duration = info["length"] / 1000


class Queue():
    def __init__(self, volume, channel):
        self.channel = channel
        self.songs = []
        self.volume = volume
        self.loop = False

    def getLength(self, player):
        if player.position != 0:
            vPosition = player.position
        else:
            vPosition = player.last_position
        totalLength = 0
        for i, song in enumerate(self.songs):
            if i == 0:
                if isinstance(song, Playlist):
                    totalLength += round(((song.getLength()) - vPosition) / 1000)
                else:
                    totalLength += round((self.songs[0].video.length - vPosition) / 1000)
            else:
                if isinstance(song, Playlist):
                    totalLength += round(((song.getLength())) / 1000)
                else:
                    totalLength += round(song.video.length / 1000)
        return totalLength

    def addSong(self, song):
        self.songs.append(song)


class Audio(commands.Cog, wavelink.WavelinkMixin):
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_   streamed 1 -reconnect_delay_max 5',
                      'options': '-vn -af loudnorm=I=-16:LRA=11:TP=-1.5'}
    queues = {}
    embedlinks = {}
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }]
    }

    def __init__(self, client):
        log(1, "Audio cog loaded")
        # self.client.lavaClient = lavalink.Client(self.client.user.id)
        # self.client.lavaClient.add_node('localhost', 7000, 'ROGB', 'na', 'mNode')
        # self.client.add_listener(self.client.lavaClient.voice_update_handler, 'on_socket_response')
        # self.client.lavaClient.add_event_hook(self.track_hook)
        log(1, f"Audio Configuration: VOLUME {CONFIG['VOLUME']}      MAX-DESC {CONFIG['DESCRIPTION_MAX']}")
        self.client = client
        self.scAPI = SoundcloudAPI()
        self.client.wavelink = wavelink.Client(bot=self.client)
        self.client.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        self.spotifyClient = await StY.PYTClient.create_client(spotifyID="0089f2bbc13f439f9cadde1db6069600",
                                                               spotifySecret="04e373ec4ed14cdea7518896ef07a74a")
        await self.client.wait_until_ready()

        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
        # await self.client.wavelink.initiate_node(host='localhost',
        #                                          port=80,
        #                                          rest_uri='http://localhost:80',
        #                                          password='youshallnotpass',
        #                                          identifier='TEST',
        #                                          region='us_central')
        config = utils.getConfig()
        host = str(config[4][:-1])
        port = str(config[5])
        await self.client.wavelink.initiate_node(host=host,
                                                 port=port,
                                                 rest_uri=f'http://{host}:{port}',
                                                 password='youshallnotpass',
                                                 identifier='ROGUE 1',
                                                 region='europe')

    # async def track_hook(self, event):
    #     if isinstance(event, lavalink.events.QueueEndEvent):
    #         guild_id = int(event.player.guild_id)
    #         await self.connect_to(guild_id, None)

    # -----------------OLD COOLDOWN SYSTEM START-------------------------
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

    @wavelink.WavelinkMixin.listener()
    async def on_track_end(self, node: wavelink.Node, payload):
        player = payload.player
        guildID = player.guild_id
        if not payload.reason == "REPLACED":
            try:
                if isinstance(self.queues[guildID].songs[0], Playlist):
                    song = await self.queues[guildID].songs[0].next()
                    if song is None:
                        self.queues[guildID].songs.pop(0)
                elif self.queues[guildID].loop == False:  # if no loop
                    self.queues[guildID].songs.pop(0)  # no song in queue
                    if isinstance(self.queues[guildID].songs[0], Playlist): #initialize playlist if playlist comes after song
                        song = await self.queues[guildID].songs[0].next()
            except:
                pass  # empty queue
            else:
                if player is not None:
                    if len(self.queues[guildID].songs) > 0:  # if there is a song then play
                        if isinstance(self.queues[guildID].songs[0], Playlist):
                            embed = discord.Embed(
                                title=f':play_pause: [PLAYLIST {self.queues[guildID].songs[0].cPosition+1}/{self.queues[guildID].songs[0].videoCount}] Now playing - "{self.queues[guildID].songs[0].video}"')
                            if isinstance(self.queues[guildID].songs[0], YTPlaylist):
                                eColor = discord.Colour.dark_red()
                            elif isinstance(self.queues[guildID].songs[0], SCPlaylist):
                                eColor = discord.Colour.dark_orange()
                            else:
                                eColor = discord.Colour.dark_green()
                            embed.colour = eColor
                            await self.queues[guildID].channel.send(embed=embed)
                            await player.play(self.queues[guildID].songs[0].video)
                        else:
                            if not self.queues[guildID].loop:
                                embed = discord.Embed(
                                    title=f':play_pause: Now playing - "{self.queues[guildID].songs[0].title}"')
                                if isinstance(self.queues[guildID].songs[0], YTSong):
                                    eColor = discord.Colour.dark_red()
                                elif isinstance(self.queues[guildID].songs[0], SCSong):
                                    eColor = discord.Colour.dark_orange()
                                else:
                                    eColor = discord.Colour.dark_green()
                                embed.colour = eColor
                                await self.queues[guildID].channel.send(embed=embed)
                            await player.play(self.queues[guildID].songs[0].video)
                else:
                    self._stopVC(self.client.get_guild(guildID))

    async def playQueue(self, ctx, boundChannel):  # start going through the queue
        # def moveToNext():
        #     print("ew")
        #     # try:
        #     #     if self.queues[ctx.guild.id].loop == False: #if no loop
        #     #         self.queues[ctx.guild.id].songs.pop(0) #no song in queue
        #     # except:pass #empty queue
        # else:
        #     player = self.client.wavelink.get_player(ctx.guild.id)
        #     if player is not None:
        #         if len(self.queues[ctx.guild.id].songs) > 0: #if there is a song then play
        #             if not self.queues[ctx.guild.id].loop:
        #                 self.client.loop.create_task(ctx.send(embed=discord.Embed(title=f':play_pause: Now playing - "{self.queues[ctx.guild.id].songs[0].title}"', color=discord.Colour.dark_red())))
        #             volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
        #             volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
        #             await player.play(self.queues[ctx.guild.id].songs[0].vi

        #         else: #if not
        #             moveToNext()
        #     else:
        #         self._stopVC(ctx)

        player = self.client.wavelink.get_player(ctx.guild.id)
        if isinstance(self.queues[ctx.guild.id].songs[0], Playlist):
            track = await self.queues[ctx.guild.id].songs[0].next()
        else:
            track = self.queues[ctx.guild.id].songs[0].video
        await player.set_volume(50)
        await player.play(track)
        # volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
        # volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
        # ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())

    @staticmethod
    def userVCState(ctx):
        return ctx.message.author.voice != None

    @commands.command()
    async def initializeAudioNode(self, ctx, *args):
        if ctx.message.author.id == 234478395222654976:
            try:
                if len(args) == 3:
                    password = args[2]
                else:
                    password = "youshallnotpass"
                await ctx.send("Restarting audio player and clearing all queue instances....")
                self.queues = {}
                await ctx.send("Disconnecting from previous audio node....")
                await self.client.wavelink.destroy_node(identifier="ROGUE 1")
                if password == "youshallnotpass":
                    await ctx.send(f"Connecting to {args[0]}:{args[1]} with default password....")
                else:
                    await ctx.send(f"Connecting to {args[0]}:{args[1]} with password {password}....")
                await self.client.wavelink.initiate_node(host=args[0],
                                                         port=args[1],
                                                         rest_uri=f'http://{args[0]}:{args[1]}',
                                                         password="youshallnotpass",
                                                         identifier='ROGUE 1',
                                                         region='europe')
            except Exception as e:
                await ctx.send(f"An error occured while connecting the new audio node: \n{str(e)}")
            else:
                await ctx.send(f"Connected!\n")
        else:
            await ctx.send(f"You are not allowed to access this command.")

    @commands.command(aliases=["forward"])
    @commands.check(userVCState.__func__)
    async def forwards(self, ctx, *args):
        player = self.client.wavelink.get_player(ctx.guild.id)
        try:
            if int(args[0]) > 0:
                args = int(args[0]) * 1000
            else:
                raise ValueError
        except:
            await ctx.send(
                "You typed an invalid argument. The amount you want to forward/go backwards in the song should be in seconds, and should not exceed the song's time.")
        else:
            if await self.checkChannel(ctx):
                if player.is_playing:
                    songLength = self.queues[ctx.guild.id].songs[0].video.length
                    pPosition = player.position
                    if pPosition + args < songLength:
                        await player.seek(round(pPosition + args))
                        await ctx.message.add_reaction("👍")
                    else:
                        await ctx.send("The amount you typed exceeded the song's time.")
                else:
                    await ctx.send("The bot isn't playing anything.")

    @commands.command()
    async def volume(self, ctx, arg):
        player = self.client.wavelink.get_player(ctx.guild.id)
        await player.set_volume(int(arg))
        await ctx.message.add_reaction("👍")

    @commands.command(aliases=["backward"])
    @commands.check(userVCState.__func__)
    async def backwards(self, ctx, *args):
        player = self.client.wavelink.get_player(ctx.guild.id)
        try:
            if int(args[0]) > 0:
                args = int(args[0]) * 1000
            else:
                raise ValueError
        except:
            await ctx.send(
                "You typed an invalid argument. The amount you want to forward/go backwards in the song should be in seconds, and should not exceed the song's time.")
        else:
            if await self.checkChannel(ctx):
                if player.is_playing:
                    pPosition = player.position
                    if pPosition - args > 0:
                        await player.seek(round(pPosition - args))
                        await ctx.message.add_reaction("👍")
                    else:
                        await ctx.send("The amount you typed exceeded the song's time.")
                else:
                    await ctx.send("The bot isn't playing anything.")

    @commands.command()
    @commands.check(userVCState.__func__)
    async def pause(self, ctx):
        if await self.checkChannel(ctx):
            await self.client.wavelink.get_player(ctx.guild.id).set_pause(True)
            await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.check(userVCState.__func__)
    async def resume(self, ctx):
        if await self.checkChannel(ctx):
            await self.client.wavelink.get_player(ctx.guild.id).set_pause(False)
            await ctx.message.add_reaction("👍")

    async def checkChannel(self, ctx):
        if self.client.wavelink.get_player(ctx.guild.id).channel_id != ctx.author.voice.channel.id:
            await ctx.send(
                "You are not connected to the same channel as the bot or the bot is not connected to a channel.")
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
            if isinstance(self.queues[ctx.guild.id].songs[0], Playlist):
                await ctx.send(f'Looping is not currently supported on playlists.')
            else:
                self.queues[ctx.guild.id].loop = True
                await ctx.send(
                    f'Started looping "**{self.queues[ctx.guild.id].songs[0].title}**". To stop looping, type !stoploop or to skip the song, type !skip')

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
            await self.client.wavelink.get_player(ctx.guild.id).stop()
            if isinstance(self.queues[ctx.guild.id].songs[0], Playlist):
                title = self.queues[ctx.guild.id].songs[0].video
                footerText = "A playlist is currently playing. To skip the playlist, use !skippl"
            else:
                title = self.queues[ctx.guild.id].songs[0].title
                footerText = None
            embed = discord.Embed(title=f':track_next: Skipped "{title}"')
            if footerText:
                embed.set_footer(text=footerText)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(userVCState.__func__)
    async def skippl(self, ctx):
        if await self.checkQueue(ctx) and await self.checkChannel(ctx):
            if isinstance(self.queues[ctx.guild.id].songs[0], Playlist):
                title = str(self.queues[ctx.guild.id].songs[0].title)
                self.queues[ctx.guild.id].songs[0] = None
                await self.client.wavelink.get_player(ctx.guild.id).stop()
                embed = discord.Embed(title=f':track_next: Skipped playlist "{title}"')
                await ctx.send(embed=embed)
            else:
                await ctx.send("A playlist is not currently playing.")

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
                    if len(self.queues[ctx.guild.id].songs) >= num >= 1:  # queue starts at number 1, not 0
                        await ctx.send(f':ok_hand: Removed "{self.queues[ctx.guild.id].songs[num].title}"')
                        self.queues[ctx.guild.id].songs.pop(num)
                    else:
                        if num == 0:
                            await ctx.send(
                                "If you meant to skip the song, use !skip. Otherwise, choose a number between 1 and the amount of songs.")
                        else:
                            await ctx.send(
                                f"There are {len(self.queues[ctx.guild.id].songs) - 1} songs in the queue, excluding the one currently playing. Please choose a number between 1 and {len(self.queues[ctx.guild.id].songs) - 1}.")
            else:
                await ctx.send("There are no songs in the queue.")

    @commands.Cog.listener()  # Voice_State listener
    async def on_voice_state_update(self, member, before, after):  # Voice_State listener
        cGuild = self.client.get_guild(member.guild.id)
        vClient = self.client.wavelink.get_player(member.guild.id)
        vChannel = self.client.get_channel(vClient.channel_id)
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
                    if len(vChannel.members) == 1:
                        self._stopVC(cGuild)
                    # else:
                    #     if vClient.position == 0:
                    #         vPosition = vClient.last_position
                    #     else:
                    #         vPosition = vClient.position
                    #     await vClient.connect(after.channel.id)
                    #     await vClient.play(self.queues[member.guild.id].songs[0].video, start=round(vPosition))
                elif not after.channel and before.channel:
                    if self.queues.get(member.guild.id):
                        self._stopVC(cGuild)
        elif member.id != self.client.user.id and vClient and vClient.is_connected and (
                before.channel == vChannel or after.channel == vChannel):
            if before.channel and before.channel == vChannel:  # if user  our channel
                if len(vChannel.members) == 1:
                    if vClient.is_playing == True:
                        await asyncio.sleep(45)
                    else:
                        await asyncio.sleep(20)
                    if len(vChannel.members) == 1:
                        self._stopVC(cGuild)

    def _stopVC(self, guild):  # can either send guild or context
        vClient = self.client.wavelink.get_player(guild.id)
        if guild is discord.ext.commands.context:  # if CONTEXT
            guild = guild.guild
        if vClient:
            self.client.loop.create_task(vClient.destroy())
        try:
            self.queues.pop(guild.id)
        except:
            pass

    @commands.command(aliases=["disconnect", "stop", "die", "quit", "kys", "commit_sepuku", "kill_joseph"])
    @commands.check(userVCState.__func__)
    async def leave(self, ctx):
        if await self.checkChannel(ctx):
            vClient = self.client.wavelink.get_player(ctx.guild.id)
            if vClient:
                if vClient:
                    self.client.loop.create_task(vClient.destroy())
                try:
                    self.queues.pop(ctx.guild.id)
                except:
                    pass
            else:
                await ctx.send("The bot isn't currently in a voice channel.")

    @staticmethod
    async def getLength(duration):
        if int(duration / 60) == 0:
            return f'{str(duration % 60) + "s"}'
        else:
            return f'{str(int(duration / 60)) + "m"} {str(duration % 60) + "s"}'

    # async def getVideoEmbed(self, video, ctx):
    #     embed = discord.Embed(title=unescape(video['title']), url=video['link'], color=discord.Colour.red())
    #     try:
    #         if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
    #             totalLength = self.queues[ctx.guild.id].getLength()
    #             embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
    #     except:pass
    #     if 'descriptionSnippet' in video and len(video['descriptionSnippet'][0]['text']) > CONFIG["DESCRIPTION_MAX"]:
    #         description = unescape(video['descriptionSnippet'][0]['text'])[:CONFIG["DESCRIPTION_MAX"]] + "...."
    #     elif 'descriptionSnippet' not in video:
    #         description = None
    #     else:
    #         description = unescape(video['descriptionSnippet'][0]['text'])
    #     embed.set_thumbnail(url=video['thumbnails'][0]['url'])
    #     embed.add_field(name="Duration", value=video['duration'], inline=True)
    #     embed.add_field(name="Uploaded By", value=str(unescape(video["channel"]['name'])), inline=True)
    #     embed.add_field(name="Views", value=video['viewCount']['short'], inline=True)
    #     if description is not None:
    #         embed.add_field(name="Description", value=description, inline=True)
    #     return embed

    async def getVideoEmbed(self, video, ctx):
        if isinstance(video, YTSong):
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.red())
            embed.set_author(name="YouTube", url="https://www.youtube.com/",
                             icon_url="https://i.pinimg.com/originals/31/23/9a/31239a2f70e4f8e4e3263fafb00ace1c.png")
            try:
                if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
                    totalLength = self.queues[ctx.guild.id].getLength(self.client.wavelink.get_player(ctx.guild.id))
                    embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
            except:
                pass
            if video.description is not None and len(video.description) > CONFIG["DESCRIPTION_MAX"]:
                description = unescape(video.description)[:CONFIG["DESCRIPTION_MAX"]] + "...."
            elif video.description is None:
                description = None
            else:
                description = unescape(video.description)
            embed.set_thumbnail(url=video.image)
            embed.add_field(name="Duration", value=video.duration, inline=True)
            embed.add_field(name="Uploaded By",
                            value=f'[{str(unescape(video.channelName))}]({str(unescape(video.channelLink))})',
                            inline=True)
            embed.add_field(name="Views", value=video.views, inline=True)
            if description is not None:
                embed.add_field(name="Description", value=description, inline=True)
            return embed
        elif isinstance(video, SpotifySong):
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.dark_green())
            embed.set_author(name="Spotify", url="https://www.spotify.com/",
                             icon_url="https://i.pinimg.com/originals/7a/ec/a5/7aeca525afa2209807c15da821b2f2c6.png")
            try:
                if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
                    totalLength = self.queues[ctx.guild.id].getLength(self.client.wavelink.get_player(ctx.guild.id))
                    embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
            except:
                pass
            embed.set_thumbnail(url=video.image)
            embed.set_footer(text="Not the right song? Try playing a YouTube or a Soundcloud song for more accurate results. To learn more why this happens visit this link.")
            embed.add_field(name="Duration", value=await Audio.getLength(video.duration), inline=True)
            embed.add_field(name="Artists", value=video.artistStr, inline=True)
            embed.add_field(name="Popularity", value=video.popularity, inline=True)
            return embed
        elif isinstance(video, YTPlaylist):
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.dark_red())
            embed.set_author(name="YouTube - Playlist", url="https://www.youtube.com/",
                             icon_url="https://i.pinimg.com/originals/31/23/9a/31239a2f70e4f8e4e3263fafb00ace1c.png")
            try:
                if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
                    totalLength = self.queues[ctx.guild.id].getLength(self.client.wavelink.get_player(ctx.guild.id))
                    embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
            except:
                pass
            embed.set_thumbnail(url=video.image)
            embed.add_field(name="Video Count", value=video.videoCount, inline=True)
            embed.add_field(name="Uploaded By", value=f'[{str(unescape(video.channelName))}]({str(unescape(video.channelLink))})', inline=True)
            return embed
        elif isinstance(video, SCPlaylist):
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.orange())
            embed.add_field(name="Track Count", value=str(video.videoCount), inline=True)
            embed.set_author(name="SoundCloud - Playlist", url="https://soundcloud.com/",
                             icon_url="https://i.pinimg.com/originals/47/6b/c8/476bc8fd4f4a353fbf431bf1ad2c70e1.jpg")
            return embed
        elif isinstance(video, SpotifyPlaylist):
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.dark_green())
            embed.set_author(name="Spotify - Playlist", url="https://www.spotify.com/",
                             icon_url="https://i.pinimg.com/originals/7a/ec/a5/7aeca525afa2209807c15da821b2f2c6.png")
            try:
                if len(self.queues[ctx.guild.id].songs) > 0 and self.queues[ctx.guild.id].loop == False:
                    totalLength = self.queues[ctx.guild.id].getLength(self.client.wavelink.get_player(ctx.guild.id))
                    embed.set_footer(text=f"Estimated time until playing: {await self.getLength(totalLength)}")
            except:
                pass
            embed.set_thumbnail(url=video.image)
            embed.add_field(name="Track Count", value=str(video.videoCount), inline=True)
            if hasattr(video, "followers"):
                embed.add_field(name="Followers", value=video.followers, inline=True)
            if hasattr(video, "popularity"):
                embed.add_field(name="Popularity", value=f"{video.popularity}/100", inline=True)
            return embed
        else:
            embed = discord.Embed(title=unescape(video.title), url=video.url, color=discord.Colour.orange())
            embed.set_author(name="SoundCloud", url="https://soundcloud.com/",
                             icon_url="https://i.pinimg.com/originals/47/6b/c8/476bc8fd4f4a353fbf431bf1ad2c70e1.jpg")
            return embed

    async def search(self, ctx, arg):  # searches by string argument and returns a youtube link
        vClient = self.client.wavelink.get_player(ctx.guild.id)
        searchMessage = await ctx.send("**Searching...**")

        def checkResponse(message):
            return message.channel == ctx.channel and message.author == ctx.author

        search = yt.VideosSearch(arg, limit=5).resultComponents
        for i, searchResult in enumerate(search):
            if not searchResult.get('duration'): #no livestreams allowed
                search.pop(i)
        await searchMessage.delete()
        if len(search) == 0:
            await ctx.send("No results were found. Try a different song name.")
            return -1
        sendStr = "**Choose Video** (type the video's number)\n"
        for i, video in enumerate(search):
            sendStr += f"{i + 1}. {unescape(video['title'])}\n"
        await ctx.send(sendStr)
        while (True):
            try:
                response = await self.client.wait_for('message', timeout=360, check=checkResponse)
            except:
                if vClient and not ctx.guild.voice_client.is_playing:
                    await ctx.guild.voice_client.disconnect()
                    self.queues.pop(ctx.guild.id)
                    return -1
            else:
                try:
                    response = int(response.content)
                except:
                    response = response.content.split(" ")[0]
                    if response.lower() == "!play" or response.lower() == "!p" or response.lower() == "!youtube":  # check if there is already another search. if so then don't add
                        return -1
                    pass
                else:
                    player = self.client.wavelink.get_player(ctx.guild.id)
                    if not player.is_connected:
                        await ctx.send(
                            "The bot isn't connected to a voice channel anymore, and therefore your search selection could not be completed. Please search for the song again to make the bot join your channel.")
                        return -1
                    elif len(search) >= response >= 1:
                        return search[response - 1]
                    else:
                        await ctx.send("You typed an invalid selection. Search for the song again. ")
                        return -1

    # @commands.command()
    # async def ytinfo(self, ctx, *args):
    #     if "watch?v" not in args[0].lower():
    #         url = " ".join(args)
    #         search = await self.search(ctx, url)
    #     else:
    #         search = args[0]
    #     video = await self.createSong(search)
    #     embed = await self.getVideoEmbed(video, ctx)
    #     embed.set_footer(text="Just type !play (no name required) to play this song.")
    #     await ctx.send(embed=embed)
    #     self.embedlinks[ctx.guild.id] = search

    # async def createSong(self, url, info=None):
    #     if info is None:
    #         with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
    #             info = ydl.extract_info(url=url, download=False)
    #     song = Song(info['formats'][0]['url'], url, info['title'], description=info["description"], image=info["thumbnail"], views=info["view_count"], duration=info["duration"], date=info["upload_date"], channel=info["uploader"])
    #     return song

    @commands.command()
    @commands.check(userVCState.__func__)
    async def clear(self, ctx):
        if await self.checkQueue(ctx) and await self.checkChannel(ctx):
            length = len(self.queues[ctx.guild.id].songs)
            if length > 1:
                self.queues[ctx.guild.id].songs = [self.queues[ctx.guild.id].songs[0]]
                await ctx.message.add_reaction("👍")
                await ctx.send(f"Cleared {length-1} songs/playlists from the queue!")
            else:
                await ctx.send("There is nothing to clear. (there are no songs queued to play)")

    async def resolveSearch(self, ctx, args):
        lowArgs = args[0].lower()
        searchType = None
        if "watch?v" in lowArgs or "playlist?list" in lowArgs:
            if "watch?v" in lowArgs:
                if "list=" in lowArgs:
                    pID = parse.parse_qs(parse.urlparse(args[0]).query)
                    search = yt.Playlist.get(f"https://www.youtube.com/playlist?list={pID['list'][0]}")
                    return search, "youtube", "playlist"
                else:
                    search = yt.VideosSearch(args[0], limit=1)
                    search = search.resultComponents[0]
                    return search, "youtube", "video"
            else:
                search = yt.Playlist.get(args[0])
                return search, "youtube", "playlist"
        elif "soundcloud.com" in lowArgs:
            if "set" in lowArgs:
                return lowArgs, "soundcloud", "playlist"
            else:
                return lowArgs, "soundcloud", "video"
        elif "spotify.com" in lowArgs:
            return args[0], "spotify", "video"
        else:
            url = " ".join(args)
            search = await self.search(ctx, url)
            return search, "youtube", "video"

    async def createSongYT(self, data):
        track = await self.client.wavelink.get_tracks(data["link"])
        track = track[0]
        song = YTSong(track, data["link"], video=data)
        return song

    async def createSongSC(self, link):
        track = await self.client.wavelink.get_tracks(link)
        track = track[0]
        song = SCSong(track, track.info["uri"])
        return song

    async def createSP(self, link):
        trackType, trackID = StY.PYTClient.resolveSpotifyUrl(link)
        if trackType == "playlist":
            songs, playlist = await self.spotifyClient.getPlaylist(trackID)
            return SpotifyPlaylist(songs, link, playlist, self.client)
        elif trackType == "album":
            type, album, songs = await self.spotifyClient.getAlbum(trackID, self.client)
            if type == "single":
                return SpotifySong(album, songs['external_urls']['spotify'], songs)
            elif type == "album":
                return SpotifyPlaylist(album, link, songs, self.client)
        elif trackType == "track":
            track, url, sTrack = await self.spotifyClient.getSong(trackID, self.client)
            return SpotifySong(track, url, sTrack)
        else:
            return -1

    async def createPlaylistYT(self, data):
        tracks = await self.client.wavelink.get_tracks(data["link"])
        playlist = YTPlaylist(data, tracks, data["link"])
        return playlist

    async def createPlaylistSC(self, link):
        wavelink = self.client.wavelink
        track = await wavelink.get_tracks(link)
        song = SCPlaylist(track, link)
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
                    fieldNames[0] = '**[LOOP]** ' + fieldNames[0]
                if isinstance(songs[0], Playlist):
                    fieldNames[0] = f'**[PLAYLIST {songs[0].cPosition+1}/{songs[0].videoCount}]** ' + fieldNames[0]
                embed = discord.Embed(title="**Current Queue**")
                embed.set_footer(
                    text=f"Estimated time for entire queue: {await self.getLength(self.queues[ctx.guild.id].getLength(self.client.wavelink.get_player(ctx.guild.id)))}")
                embed.add_field(name="Currently Playing", value=fieldNames[0])
                def returnStr():
                    str = ""
                    for i, title in enumerate(fieldNames[1:]):
                        if isinstance(songs[i], Playlist):
                            str += f"{i + 1}. **[PLAYLIST {songs[i+1].videoCount} SONGS]** {title}\n"
                        else:
                            str += f"{i + 1}. {title}\n"
                    return str

                if len(fieldNames) > 1:
                    embed.add_field(name="In Queue", value=returnStr(), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("The queue is currently empty.")

    @commands.command(aliases=["p", "youtube", "music", "P", "PLAY"])
    @commands.check(commands.has_permissions(manage_messages=True))
    @commands.check(userVCState.__func__)
    async def play(self, ctx, *args):
        vClient = self.client.wavelink.get_player(ctx.guild.id)
        vChannel = self.client.get_channel(vClient.channel_id)
        if len(args) > 0 or (ctx.guild.id in self.embedlinks.keys()):
            if vClient and vChannel == ctx.message.author.voice.channel:  # if connected to the right channel
                pass
            elif vClient.is_connected:
                if vClient.is_playing:
                    await ctx.send(
                        "The bot is currently **playing a song** in another channel. Before joining a new channel, tell it to stop playing in the other channel by typing !leave. ")
                    return
                else:
                    await vClient.disconnect()
                    self.queues.pop(ctx.guild.id)
                    await vClient.connect(ctx.message.author.voice.channel.id)
            elif self.userVCState(ctx):
                await vClient.connect(ctx.message.author.voice.channel.id)
            else:
                await ctx.send("You are not in a voice channel.")
                return
            if (len(args) > 0):
                search, searchPlatform, searchType = await self.resolveSearch(ctx, args)
            else:
                search, searchPlatform, searchType = await self.resolveSearch(ctx, self.embedlinks.pop(ctx.guild.id))
            if search != -1:
                player = self.client.wavelink.get_player(ctx.guild.id)
                if player.is_playing:
                    await ctx.send("**Adding to Queue**\n")
                else:  # just checking whether the loop is still running (if more the one song then it must be running)
                    await ctx.send("**Now Playing**\n")
                if searchPlatform == "youtube":
                    if searchType == "video":
                        song = await self.createSongYT(search)
                    else:
                        song = await self.createPlaylistYT(search)
                elif searchPlatform == "soundcloud":
                    if searchType == "video":
                        song = await self.createSongSC(search)
                    else:
                        song = await self.createPlaylistSC(search)
                elif searchPlatform == "spotify":
                    song = await self.createSP(search)
                else:
                    raise invalidTypeError
                embed = await self.getVideoEmbed(song, ctx)
                await ctx.send(embed=embed)
                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = Queue(CONFIG["VOLUME"], ctx.channel)
                self.queues[ctx.guild.id].addSong(song)
                if not player.is_playing:
                    await self.playQueue(ctx, player.channel_id)
        else:
            await ctx.send("Please provide a search query or a Spotify, SoundCloud, or YouTube link to play.")