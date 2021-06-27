import discord
from discord.ext import commands, ipc
import log
import json
import utils


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
            log.log(1, f"IPC SECRET: {IPC_SECRET}")

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
        await client.change_presence(activity=discord.Game(f"Running V{VERSION} | !help"))

    client.ipc.start()
    client.run(config[0])

if __name__ == "__main__":
    utils.splash()
    main()