import discord
from discord.ext import commands
import configtools
import ast
from log import log
import Audio

links = {
    "admin":""
}

class Admin(commands.Cog):
    configlines = {
        "password": 0,
        "admins": 1,
        "volume": 2,
        "description_max":3
    }
    def __init__(self, client, configFile):
        log(1, "Admin cog loaded")
        self.client = client
        self._last_member = None
        self.configFile = configFile

    @commands.command(aliases=["admincommand", "administrator"])
    async def admin(self, ctx, *args):
        if await self.verifyAdmin(ctx) and len(args) > 0:
            # ---------------add admin----------------
            if args[0] == "add" or args[0] == "addAdmin": #add admin
                try:
                    adminAddState = await self.addAdmin(args[1])
                except:
                    await ctx.send(f"Error - invalid parameters or internal malfunction. See admin documentation - {links['admin']}")
                else:
                    if adminAddState:
                        await ctx.send(f"Added admin {args[1]}")
                    else:
                        await ctx.send(f"{args[1]} already exists in admin list.")

            # ---------------remove admin----------------
            elif args[0] == "remove" or args[0] == "removeAdmin":
                try:
                    argument = ast.literal_eval(args[1])
                except: #if string
                    adminRemoveState = await self.removeAdmin(args[1])
                    if adminRemoveState:
                        await ctx.send(f"Admin {args[1]} successfully removed")
                    else:
                        await ctx.send(f"Admin could not be found in the administrator list.")
                else: #if not string
                    try:
                        adminName = self.removeAdmin(adminIndex=argument-1)
                    except:
                        await ctx.send(f"Error - Admin could not be found in the administrator list, or the type that was entered was not referencing the administrator name or adminlist ID. See admin documentation - {links['admin']}")
                    else:
                        await ctx.send(f"Admin {adminName} successfully removed")

            #list admins
            elif args[0] == "list":
                adminlist = self.configFile.getConfigEntry(self.configlines["admins"], True)
                sendString = ""
                for i, admin in enumerate(adminlist):
                    sendString += f"{i+1}. {admin}\n"
                await ctx.send(f"**Admin List - **\n{sendString}")

            # elif args[0] == "volume":
            #     if type(ast.literal_eval(args[1])) == float or type(ast.literal_eval(args[1])) == int:
            #         await self.changeVolume(args[1])
            #     else:
            #         await ctx.send("Invalid param")
            # elif args[0] == "description":
            #     if type(ast.literal_eval(args[1])) == int:
            #         await self.changeDescriptionMax(args[1])
            #     else:
            #         await ctx.send("Invalid param")
            else:
                await ctx.send(f"Invalid parameter count. Please see {links['admin']}")

    async def verifyAdmin(self, ctx):
        def checkResponse(message):
            return ctx.channel == message.channel
        adminList = self.configFile.getConfigEntry(self.configlines["admins"], True)
        for admin in adminList:
            if admin == str(ctx.author):
                return True
        loop_continue = True
        await ctx.send("You are not found to be an administrator. Please specify the global administration password or add an entry to the admin list found in LOCALAPPDATA")
        while loop_continue:
            try:
                response = await self.client.wait_for('message', check=checkResponse, timeout=360)
            except:
                await ctx.send("Timeout reached for sending admin password.")
                return False
            else:
                if str(self.configFile.getConfigEntry(self.configlines["password"])) == response.content:
                    await self.addAdmin(ctx.author)
                    await ctx.send(f"Added {str(ctx.author)} as an administrator. ")
                    return True
                else:
                    await ctx.send("You entered an incorrect password. Would you like to try again?")
                    try:
                        response = await self.client.wait_for('message', check=checkResponse, timeout=360)
                    except:
                        await ctx.send("Timeout reached for sending admin password.")
                    else:
                        if response.content.lower() == "yes" or response.content.lower() == "y":
                            await ctx.send("Enter password - ")
                            continue
                        else:
                            loop_continue = False
                            await ctx.send("Received no")
                            return False

    @commands.command()
    async def stopexecution(self, ctx):
        if await self.verifyAdmin(ctx):
            def checkResponse(message):
                return ctx.channel == message.channel
            await ctx.send("Are you sure you want to the execution of the bot in all servers?")
            try:
                message = await self.client.wait_for('message', check=checkResponse, timeout=360)
            except:
                await ctx.send("Timeout for stop execution reached.")
            else:
                if message == "yes" or message == "y":
                    self.client.stop()
    async def getDescriptionMax(self):
        return self.configFile.getConfigEntry(self.configlines["description_max"])

    async def getVolume(self):
        return self.configFile.getConfigEntry(self.configlines["volume"])

    async def changePass(self, newPass):
        self.configFile.editConfigEntry(self.configlines["password"], value=newPass)

    async def changeVolume(self, volume):
        self.configFile.editConfigEntry(self.configlines["volume"], value=volume)
        # import Audio
        # Audio.update()

    async def changeDescriptionMax(self, max):
        self.configFile.editConfigEntry(self.configlines["description_max"], value=max)
        # import Audio
        # Audio.CONFIG["VOLUME"] = max

    async def getPass(self):
        return self.configFile.getConfigEntry(self.configlines["password"])

    async def addAdmin(self, adminName):
        adminlist = self.configFile.getConfigEntry(self.configlines["admins"], True)
        for admin in adminlist:
            if admin == adminName:
                return False
        self.configFile.editConfigEntry(self.configlines["admins"], value=str(adminName), listType="add")
        return True

    async def removeAdmin(self, adminName="", adminIndex=-1):
        if adminName != None and adminIndex != None:
            if adminName != None:
                adminlist = self.configFile.getConfigEntry(self.configlines["admins"], True)
                for index, admin in enumerate(adminlist):
                    if admin == adminName:
                        self.configFile.editConfigEntry(self.configlines["admins"], listType="remove", listIndex=index)
                        return adminName
                return False
            elif adminIndex != None:
                adminName = self.configFile.getConfigEntry(self.configlines["admins"], True)[adminIndex]
                self.configFile.editConfigEntry(self.configlines["admins"], listType="remove", listIndex=adminIndex)
                return adminName
        else:
            return False