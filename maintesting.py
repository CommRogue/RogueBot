import discord
from discord.ext import commands, ipc
import json

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self, secret_key="ROGB", port=8735, do_multicast=False)

    async def on_ready(self):
        """Called upon the READY event"""
        print("Bot is ready.")

    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)


my_bot = MyBot(command_prefix="!", intents=discord.Intents.all())

@my_bot.ipc.route()
async def get_member(data):
    member = my_bot.get_user(data.id)  # get the guild object using parsed guild_id
    member = {"avatar":member.avatar_url, "display_name":member.display_name, "discriminator":member.discriminator, "mention":member.mention, "bot":member.bot}
    return member  # return the member count to the client

@my_bot.ipc.route()
async def get_member_count(data):
    guild = my_bot.get_guild(
        data.guild_id
    )  # get the guild object using parsed guild_id

    return guild.member_count  # return the member count to the client

@my_bot.ipc.route()
async def get_servers(data):
    guilds = my_bot.guilds
    names = list(map(lambda guild: guild.name, guilds))
    return names


if __name__ == "__main__":
    my_bot.ipc.start()  # start the IPC Server
    my_bot.run("NzgwNzQzMjM5NjAxNzUwMDE3.X7zhzQ.Z8OItvQFxmG8C1IXZyBGiV7_jNg")