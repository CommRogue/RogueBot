from discord.ext import ipc
import asyncio
import logging
import json

ipc_client = ipc.Client(
    secret_key="ROGB",
    port=8735
)

logging.getLogger('asyncio').setLevel(logging.CRITICAL)

async def index():
    servers = await ipc_client.request("get_member_count", guild_id=791953226719166477)
    servers = json.loads(servers)
    print(str(servers))
    print("e")

asyncio.get_event_loop().run_until_complete(index())