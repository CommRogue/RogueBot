import discord
import asyncio
import threading
from discord.ext import commands, ipc
import log
import Admin
import AudioLava as Audio
import json
import aiohttp
import ast
from collections import Counter
from Users import GuildMember
import Game
import utils
import Weather
import inspirobot
import Chess
import configtools
import serverside
# from discord_slash import cog_ext
# from discord_slash import SlashCommand
# from discord_slash.utils import manage_commands
import asyncio

config = utils.getConfig()

VERSION = config[1]
IPC_PORT = int(config[2])
IPC_SECRET = config[3]

def main():
    # logging.basicConfig(level=logging.INFO)
    class MyBot(commands.Bot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ipc = ipc.Server(self, secret_key=IPC_SECRET, port=IPC_PORT, do_multicast=False)  # IPC Server
            # self.load_extension("ipc")  # load the IPC Route cog
            log.log(1, "Starting IPC server")
            log.log(1, f"IPC PORT: {IPC_PORT}")
            log.log(1, f"IPC SECRET: {IPC_SECRET[:-2]}")

        async def on_ready(self):
            """Called upon the READY event"""
            log.log(1, "ready.")

        async def on_ipc_ready(self):
            """Called upon the IPC Server being ready"""
            log.log(1, "IPC READY")

        async def on_ipc_error(self, endpoint, error):
            """Called upon an error being raised within an IPC route"""
            print(endpoint, "raised", error)

    client = MyBot(command_prefix="!", intents=discord.Intents.all(), help_command=None, owner_id=234478395222654976)
    # slash = SlashCommand(client, auto_register=True)

    # guild_ids = [761552197410095125]

    @client.ipc.route()
    async def get_member_count(data):
        guild = client.get_guild(
            data.guild_id
        )  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client

    @client.ipc.route()
    async def get_servers(data):
        guilds = client.guilds
        names = list(map(lambda guild: guild.name, guilds))
        return json.dumps(names)

    @client.event
    async def on_ready():
        log.log(1, "Bot Initialized")
        # configFile = configtools.ConfigFile("Main Configuration", {0: "str", 1:"list", 2: ["int", "float"], 3:"int"})
        configFile = configtools.ConfigFile("Main Configuration", {0: "str", 1: "list"})
        client.add_cog(Admin.Admin(client, configFile))
        client.add_cog(Audio.Audio(client))
        client.add_cog(Game.Games(client))
        client.add_cog(Chess.Chess(client))
        client.add_cog(Weather.Weather(client))
        await client.change_presence(activity=discord.Game(f"Running V{VERSION} | !help"))

    links = {
        "netstat": "",
        "help": ""
    }

    clearCount=Counter()

    def clearFunc(ctx, amount, member):
        if clearCount[ctx.guild.id] <= amount and ctx.author.id == member:
            clearCount[ctx.guild.id] += 1
            return True
        return False

    # @slash.slash(name="whois", guild_ids=guild_ids, description="Tells you information about a user.", options=[manage_commands.create_option("user", "Mention to a user you want information about.", 3, True)])
    # async def whois(ctx, user):
    #     if len(ctx.message.mentions) > 0:
    #         mentioned = GuildMember(ctx.message.mentions[0])
    #         await ctx.send(embed=mentioned.getEmbed())
    #     else:
    #         await ctx.send("Please mention a member in this guild you want to get information on.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @client.command()
    async def deepthink(ctx, arg):
        data = {'image': 'https://www.telegraph.co.uk/content/dam/news/2016/09/08/107667228_beech-tree-NEWS_trans_NvBQzQNjv4BqplGOf-dgG3z4gg9owgQTXEmhb5tXCQRHAvHRWfzHzHk.jpg'}
        headers = {'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
        if arg:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post("https://api.deepai.org/api/deepdream", data=data) as r:
                    print("Ew")
        else:
            await ctx.send("A parameter that represents the link for the image is required. Please type the command as !deepthink {link}, and replace {link} with the image URL.")


    @client.command()
    async def whois(ctx):
        if len(ctx.message.mentions) > 0:
            mentioned = GuildMember(ctx.message.mentions[0])
            await ctx.send(embed=mentioned.getEmbed())
        else:
            await ctx.send("Please mention a member in this guild you want to get information on.")

    @client.command()
    async def hey(ctx, *args):
        if " ".join(args) == "whats your opinion" or " ".join(args) == "what's your opinion":
            await ctx.send("Man why the fuck u ask me what's my opinion? U racist bruh.")

    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            try:
                content = int(ctx.message.content[1])
            except:
                log.log(2, f"User '{ctx.author}' in guild '{ctx.guild}' tried to use command '{ctx.message.content}'")
            else:
                if content in range(1,5):
                    await ctx.send("Choose a video without the exclamation point. Just type out a number.")
        elif isinstance(error, commands.CheckFailure):
            if(ctx.message.content.startswith("!join") or ctx.message.content.startswith("!play")):
                await ctx.send("You are not connected to a voice channel.")
            if ctx.message.content.startswith("!clear" or "!delete" or "!bulkDel"):
                await ctx.send("You don't have sufficient permissions on this guild to perform this action.")
        else:
            raise error

    @client.command()
    async def inspire(ctx):
        quote = inspirobot.generate()
        await ctx.send(quote.url)

    # @slash.slash(name="inspire", description="Sends a totally inspiring quote for you.")
    # async def inspire(ctx):
    #     quote = inspirobot.generate()
    #     await ctx.send(content=quote.url)


    @client.command(aliases=["delete, bulkDel"])
    @commands.check(commands.has_permissions(manage_messages=True))
    async def message_delete(ctx, *args):
        try:
            amount = ast.literal_eval(args[0])
            if type(amount) != int:
                raise KeyError("valueerror")
            amount += 1 #to clear the !clear message, add plus 1 message
            memberID = None
            member = None
            if len(args) > 1:
                mentioned = ctx.message.mentions
                if len(mentioned) > 0:
                    member = mentioned[0]
                    memberID = mentioned[0].id
            if memberID == None:
                deletedCount = await ctx.channel.purge(limit=int(args[0]))
                t_message = await ctx.send(f"Cleared {len(deletedCount)} messages!")
                await asyncio.sleep(5)
                await t_message.delete()
            else: #if targeting member
                def clearFunc(Message):
                    if clearCount[ctx.guild.id] <= amount and Message.author.id == memberID:
                        clearCount[ctx.guild.id] += 1
                        return True
                    return False
                clearCount[ctx.guild.id] = 0
                while clearCount[ctx.guild.id] <= amount:
                    await ctx.channel.purge(limit=20, check=clearFunc) #go by chunks
                clearCount.pop(ctx.guild.id)
                t_message = await ctx.send(f"Cleared {amount} messages written by {str(member)}!")
                await asyncio.sleep(6)
                await t_message.delete()
        except discord.Forbidden:
            await ctx.send("I don't have sufficient permissions to clear messages. Please add the permissions Manage Messages to let me perform this action.")
        except:
            await ctx.send("Please specify a valid amount of messages to delete.")

    @client.ipc.route()
    async def get_member_count(data):
        guild = client.get_guild(
            data.guild_id
        )  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client

    @client.command()
    async def invite(ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=744251701678178334&permissions=8&scope=bot%20applications.commands")

    @client.command()
    async def help(ctx):
        await ctx.send("http://roguebot.rf.gd/")

    @client.command(aliases=["execute"])
    async def run(ctx, *args):
        await ctx.send("Dev only.")
        # args = " ".join(args)
        # args = args.replace('\n', '')
        # args = args.replace(';', '\n')
        # try:
        #     returned = str(exec(args))
        #     if returned != "None":
        #         await ctx.send(returned)
        # except Exception as exep:
        #     await ctx.send(f"**The command returned the following exception:** \n {exep}")

    # @slash.slash(name="connectionStatus", description="Connection status to the server.", options=[manage_commands.create_option("type", "Type can be ping or channels.", 3, False, [manage_commands.create_choice("ping","Specifies connection to the server."), manage_commands.create_choice("channels","Specifies connection to all channels.")])])
    # async def connectionStatus(ctx, type=''):
    #     if type == "ping" or type == "Latency":
    #         await ctx.send(content=f"Current latency is {round(client.latency * 1000)}ms\n*See Netstat Documentation -* {links['netstat']}")
    #     elif type == "channels" or type == "ch" or type == "channels":
    #         voiceChannels = ctx.guild.voice_channels
    #         textChannels = ctx.guild.text_channels
    #         printMessage = ""
    #         i = 0
    #         for channel in textChannels:  # add text channel info
    #             printMessage += f"{i + 1}. {channel.name} : **Type -** {channel.type},   **ID -** {channel.id}\n"
    #             i += 1
    #         for channel in voiceChannels:  # add voice channel info
    #             printMessage += f"{i + 1}. {channel.name} : **Type -** {channel.type},   **ID -** {channel.id}   **Bitrate** - {channel.bitrate}    **User limit** - {channel.user_limit}\n"
    #             members = channel.members
    #             if len(members) > 0:
    #                 printMessage += "Connected Members - \n"
    #                 for j, member in enumerate(members):
    #                     printMessage += f"{j + 1}. {member}"
    #             i += 1
    #         printMessage += f"\n*See Netstat Documentation -* {links['netstat']}"
    #         await ctx.send(content=printMessage)
    #     else:
    #         await ctx.send(content=f"**NETSTAT**\nLatency - {round(client.latency * 1000)}ms\nCurrent server voice region - {ctx.guild.region}\nTimeout length - {int(ctx.guild.afk_timeout / 60)} minutes\n*See Netstat Documentation -* {links['netstat']}")

    @client.command(aliases=["constatus", "constat", "conStatus", "conStat", "netstat"])
    async def connectionStatus(ctx, args=""):
        if args == "ping" or args == "latency":
            await ctx.send(f"Current latency is {round(client.latency*1000)}ms\n*See Netstat Documentation -* {links['netstat']}")
        elif args == "channels" or args == "ch" or args == "channels":
            voiceChannels = ctx.guild.voice_channels
            textChannels = ctx.guild.text_channels
            printMessage = ""
            i = 0
            for channel in textChannels: #add text channel info
                printMessage += f"{i+1}. {channel.name} : **Type -** {channel.type},   **ID -** {channel.id}\n"
                i += 1
            for channel in voiceChannels: #add voice channel info
                printMessage += f"{i+1}. {channel.name} : **Type -** {channel.type},   **ID -** {channel.id}   **Bitrate** - {channel.bitrate}    **User limit** - {channel.user_limit}\n"
                members = channel.members
                if len(members) > 0:
                    printMessage += "Connected Members - \n"
                    for j, member in enumerate(members):
                        printMessage += f"{j+1}. {member}"
                i += 1
            printMessage += f"\n*See Netstat Documentation -* {links['netstat']}"
            await ctx.send(printMessage)
        else:
            if args != "":
                await ctx.send("Detected incompatible argument... Reverting to default (no arguement). Please see the documentation for compatible arguments.")
            await ctx.send(f"**NETSTAT**\nLatency - {round(client.latency*1000)}ms\nCurrent server voice region - {ctx.guild.region}\nTimeout length - {int(ctx.guild.afk_timeout/60)} minutes\n*See Netstat Documentation -* {links['netstat']}")
    client.ipc.start()
    client.run(config[0])

if __name__ == "__main__":
    utils.splash()
    main()