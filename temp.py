import os
import distutils.util
import ast

class ConfigFile:
    switcher = {
        "int": int,
        "bool": bool,
        "str": str,
        "float": float,
        "list": list,
    }
    switcherDefaultValues = {
        "int": 0,
        "bool": False,
        "str": "DEFAULTSTRING",
        "float": 0.0,
        "list": [],
    }
    def __init__(self, name, allowedEntries, allowedConfigLines="", configDirectory=os.getenv("LOCALAPPDATA")+"\\DiscordBot", configName="config.txt"): #Defaults to bot
        if allowedConfigLines == "":
            allowedConfigLines = len(allowedEntries)
        self.name = name
        self.configIntegrityStatus = False
        self.allowedConfigLines = allowedConfigLines
        self.allowedEntries = allowedEntries
        self.configDirectory = configDirectory
        self.configPath = configDirectory+"\\"+configName
        print(f"Got config directory as directory {self.configPath}")
        self.cfgIntegrity(self.configPath, allowedEntries, True)

    def configsetup(self):
        print(f"Started config creation at {self.configDirectory}")
        if not os.path.exists(self.configDirectory): #if the path doesn't exist
            print(f"path doesn't exist making directory at {self.configDirectory}")
            try:
                os.mkdir(self.configDirectory)
                file = open(self.configPath, "w+")
                self.returnToDefault()
                file.close()
                return
            except:
                print("Error while creating configuration...")
                return
        elif not os.path.exists(self.configPath): #if path exists but file doesn't exist
            print("path exists, file doesn't exist")
            file = open(self.configPath, "w+")
            self.returnToDefault()
            file.close()
            return
        else:
            print("path and file exist")
            return


    def getConfigEntry(self, lineIndex):
        if not self.configIntegrityStatus:
            self.cfgIntegrity()
        file = open(self.configPath, "r")
        fileLines = file.readlines()
        return fileLines[lineIndex]

    def setConfigEntry(self, lineIndex, value):
        file = open(self.configPath, "r")
        l_lines = file.readlines()
        file.close()
        l_lines[lineIndex] = value
        file = open(self.configPath, "w")
        for line in l_lines:
            file.write(line)
        file.close()
        return

    def returnToDefault(self):
        file = open(self.configPath, 'w')
        i = 0
        for i in range(0, len(self.allowedEntries)):
            foundType = False
            if type(self.allowedEntries[i]) == list:
                for acceptedvalue in self.allowedEntries[i]:
                    if acceptedvalue in self.switcher.keys():
                        file.write(str(self.switcherDefaultValues[acceptedvalue])+"\n")
                        foundType = True
                        break
                if not foundType:
                    file.write(str(self.allowedEntries[i][0])+"\n")
            else:
                if self.allowedEntries[i] in self.switcher.keys():
                    file.write(str(self.switcherDefaultValues[self.allowedEntries[i]])+"\n")
                else:
                    file.write(str(self.allowedEntries[i])+"\n")
            i += 1


    def getConfigList(self):
        if not self.configIntegrityStatus:
            self.cfgIntegrity()
        file = open(self.configPath, 'r')
        l_file = file.readlines()
        for i in range(0, len(l_file)):
            if l_file[i][-1:] == "\n":
                l_file[i] = l_file[i][:-1]
            l_file[i] = l_file[i].strip()
        return l_file

    def cfgIntegrity(self, path="", acceptedValues="", setup=False):
        path = self.configPath
        acceptedValues = self.allowedEntries
        if setup == True:
            self.configsetup()
            setup = False
        file = open(self.configPath, "r")
        l_file = file.readlines()
        for i in range(0, len(l_file)):
            if l_file[i][-1:] == "\n":
                l_file[i] = l_file[i][:-1]
            l_file[i] = l_file[i].strip()
        if len(l_file) != self.allowedConfigLines:
            print("line count doesn't match allowed line count. reverting everything to default")
            self.returnToDefault()
            return False
        for i in range(0, len(l_file)): #go through file lines
            t_checked = False
            if type(acceptedValues[i]) == list:
                for acceptedValue in acceptedValues[i]: #go through list inside accepted values
                    try: #get exception if it is a string
                        fileValueWithType = ast.literal_eval(l_file[i])
                        if acceptedValue in self.switcher.keys() and type(fileValueWithType) == self.switcher[acceptedValue]: #if the current line accpeted value is found to be a type,
                                t_checked = True        #then check if the line type is equal to the actual type of the string literal found in the switcher
                                break
                        if type(fileValueWithType) == type(acceptedValue): # if they are the same type, then we can compare them
                            if acceptedValue == fileValueWithType:
                                t_checked = True
                                break
                    except:
                        if type(acceptedValue) != str:
                            pass
                        else:
                            if acceptedValue in self.switcher.keys() and self.switcherDefaultValues[acceptedValue] == l_file[i]:
                                t_checked = True
                                break
                            if acceptedValue == l_file[i]:
                                t_checked = True
                                break
            else: # if accepted values is not a list
                try:  # get exception if it is a string
                    fileValueWithType = ast.literal_eval(l_file[i])
                    if acceptedValues[i] in self.switcher.keys() and type(fileValueWithType) == self.switcher[acceptedValues[i]]:  # if the current line accpeted value is found to be a type,
                        t_checked = True                                                                                            # then check if the line type is equal to the actual type of the string literal found in the switcher
                        break
                    if type(fileValueWithType) == type(acceptedValues[i]): #if same type then we can compare
                        if acceptedValues[i] == fileValueWithType:
                            t_checked = True
                except:
                    if type(acceptedValues[i]) != str:
                        pass
                    else:
                        if acceptedValues[i] in self.switcher.keys() and self.switcherDefaultValues[acceptedValues[i]] == l_file[i]:
                            t_checked = True
                        elif acceptedValues[i] == l_file[i]:
                            t_checked = True
            if not t_checked and type(acceptedValues[i]) == list:
                self.configIntegrityStatus = False
                print(f"False config integrity at line {i+1}, resetting to default from original: {l_file[i]}")
                foundType = False
                for acceptedvalue in acceptedValues[i]:
                    if acceptedvalue in self.switcher.keys():
                        print("found type in allowed entries, resetting to the default value of the first type that was found")
                        self.setConfigEntry(i, str(self.switcherDefaultValues[acceptedvalue]) + "\n")
                        foundType = True
                        break
                if foundType == False:
                    self.setConfigEntry(i, str(self.allowedEntries[i][0])+"\n")
                self.cfgIntegrity()
                return
            elif not t_checked:
                self.configIntegrityStatus = False
                print(f"False config integrity at line {i + 1}, resetting to default from original: {l_file[i]}")
                foundType = False
                if acceptedValues[i] in self.switcher.keys():
                    print("found type in allowed entries, resetting to the default value of the first type that was found")
                    self.setConfigEntry(i, str(self.switcherDefaultValues[acceptedValues[i]]) + "\n")
                    foundType = True
                    break
                if foundType == False:
                    self.setConfigEntry(i, str(acceptedValues[i][0])+"\n")
                self.setConfigEntry(i, str(acceptedValues[i])+"\n")
                self.cfgIntegrity()
                return
        file.close()
        self.configIntegrityStatus = True
        print("Config integrity verified")
        return True

    # async def search(self, ctx, arg): #searches by string argument and returns a youtube link
    #     searchMessage = await ctx.send("**Searching...**")
    #     def checkResponse(message):
    #         return message.channel == ctx.channel and message.author == ctx.author
    #     YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    #     with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
    #         search = ydl.extract_info(f"ytsearch5:{arg}", download=False)['entries']
    #     await searchMessage.delete()
    #     sendStr = "**Choose Video** (type the video's number)\n"
    #     for i, video in enumerate(search):
    #         sendStr += f"{i + 1}. {unescape(video['title'])}\n"
    #     await ctx.send(sendStr)
    #     try:
    #         response = await self.client.wait_for('message', timeout=60, check=checkResponse)
    #     except:
    #         return -1
    #     else:
    #         video = None
    #         if len(search) >= int(response.content) >= 1:
    #             return 'https://www.youtube.com/watch?v='+search[int(response.content) - 1]["id"], search[int(response.content) - 1]
    #         else:
    #             await ctx.send("You typed an invalid selection.")
    #             return -1

    # def getAudioSource(self, ctx):
    #     with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
    #         FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
    #         info = ydl.extract_info(url=str(self.queues[ctx.guild.id][0].url), download=False)
    #         URL = info['formats'][0]['url'] # wtf
    #     audiosource = discord.FFmpegPCMAudio(URL, executable="C:\\ffmpeg\\bin\\ffmpeg.exe", **FFMPEG_OPTIONS)
    #     return audiosource, info

    # async def playQueue(self, ctx): #start going through the queue
    #     FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', #fixes socket disconnects
    #                       'options': '-vn'}
    #
    #     def moveToNext():
    #         try:
    #             self.queues[ctx.guild.id].songs.pop(0) #no song in queue
    #         except: #empty queue
    #             try:
    #                 queue = self.queues[ctx.guild.id] #see if a queue exists
    #             except:
    #                 # self._stopVC(ctx) #should never happen, for debug purposes
    #                 self.client.loop.create_task(ctx.send("DEBUG exception at queue existence"))
    #             else:
    #                 try:
    #                     while not len(self.queues[ctx.guild.id].songs) > 0:
    #                         v = ctx.guild.voice_client
    #                         if v is None:
    #                             break
    #                         v = ctx.guild.voice_client.channel.id
    #                         v = self.client.get_channel(v)
    #                         # converter = discord.ext.commands.VoiceChannelConverter()
    #                         # v = self.client.loop.create_task(converter.convert(ctx, str(v)))
    #                         # self.client.loop.create_task(asyncio.sleep(1))
    #                         # print(v.done())
    #                         # v = v.result()
    #                         if not len(v.voice_states) > 1:
    #                             self._stopVC(ctx)
    #                         else:
    #                             asyncio.run(asyncio.sleep(3))
    #                 except:
    #                     # self._stopVC(ctx)  # should never happen, for debug purposes
    #                     self.client.loop.create_task(ctx.send("DEBUG exception at asyncio container"))
    #         else: #if there is a song then play
    #             if len(self.queues[ctx.guild.id].songs) > 0:
    #                 self.client.loop.create_task(ctx.send(embed=discord.Embed(title=f':play_pause: Now playing - "{self.queues[ctx.guild.id].songs[0].title}"')))
    #                 volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
    #                 volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
    #                 ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())
    #             else:
    #                 moveToNext()
    #
    #
    #     volumesource = discord.FFmpegPCMAudio(self.queues[ctx.guild.id].songs[0].video, **FFMPEG_OPTIONS)
    #     volumesource = discord.PCMVolumeTransformer(volumesource, volume=self.queues[ctx.guild.id].volume)
    #     ctx.guild.voice_client.play(volumesource, after=lambda a: moveToNext())