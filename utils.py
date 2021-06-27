import aiohttp

async def requestJSON(link, type='get'):
    async with aiohttp.ClientSession() as session:
        if type.lower() == 'get':
            async with session.get(link) as response:
                return await response.json()
        elif type.lower() == "post":
            async with session.post(link) as response:
                return await response.json()
        else:
            return -1

def splash():
    print("""
    ██████╗  ██████╗  ██████╗ ██╗   ██╗███████╗██████╗  ██████╗ ████████╗
    ██╔══██╗██╔═══██╗██╔════╝ ██║   ██║██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
    ██████╔╝██║   ██║██║  ███╗██║   ██║█████╗  ██████╔╝██║   ██║   ██║   
    ██╔══██╗██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗██║   ██║   ██║   
    ██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝   ██║   
    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝    ╚═╝   
                                                                        """)

def getConfig():
    file = open("bot_config.txt", 'r')
    return file.readlines()