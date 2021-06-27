import requests
import discord
from discord.ext import commands
from log import log
import utils

KEY = "INSERT OPENWEATHER API KEY"

forecastLength = [0, 4]

class Weather(commands.Cog):
    def __init__(self, client):
        log(1, "Weather cog loaded")
        # if not os.path.exists("./resources"):
        #     os.mkdir("./resources")
        self.client = client

    @staticmethod
    async def updateMessage(ctx, message):
        nMessage = await ctx.fetch_message(message.id)
        return nMessage

    @staticmethod
    async def changeReactions(day, message, ctx):
        nMessage = await Weather.updateMessage(ctx, message)
        reactions = list(map(lambda reaction: str(reaction), nMessage.reactions))
        if not 0 < len(reactions) <= 2:
            await message.clear_reactions()
            reactions = ["X", "X"]
        if day == forecastLength[0]:
            if "➡" != reactions[0]:
                await message.clear_reactions()
                await message.add_reaction("➡")
        elif day == forecastLength[1]:
            if "⬅" != reactions[0]:
                await message.clear_reactions()
                await message.add_reaction("⬅")
            await message.clear_reaction("➡")
        else:
            if "⬅" != reactions[0]:
                await message.clear_reactions()
                await message.add_reaction("⬅")
                await message.add_reaction("➡")
            elif len(reactions) < 2:
                await message.add_reaction("➡")

    @staticmethod
    async def createEmbed(response, city, country, day):
        embed = discord.Embed(title=f"Weather - {city}, {country} - Day {(day+1)}", color=discord.Colour.blue())
        actualTemp = response['main']['temp'] - 273.15 #converting Kelvin to Celsius
        embed.add_field(name="Temperature", value=f"{round(actualTemp)} C")
        embed.add_field(name="Conditions", value=response["weather"][0]["description"])
        embed.add_field(name="Humidity", value=f"{response['main']['humidity']}%", inline=True)
        embed.add_field(name="Clouds", value=f"{response['clouds']['all']}%", inline=True)
        embed.add_field(name="Wind", value=f"{response['wind']['speed']}M/s at {response['wind']['deg']} degrees", inline=True)
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{str(response['weather'][0]['icon'])}@2x.png")
        return embed

    @commands.command(aliases=["forecast"])
    async def weather(self, ctx, *args):
        def weatherCheck(reaction, user, day, message):
            if day == forecastLength[0]:
                condition = str(reaction) == "➡"
            elif day == forecastLength[1]:
                condition = str(reaction) == "⬅"
            else:
                condition = str(reaction) == "➡" or str(reaction) == "⬅"
            return condition and user == ctx.author and reaction.message.id == message.id
        location = " ".join(args)
        # response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={KEY}")
        # response = response.json()
        response = await utils.requestJSON(f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={KEY}", 'get')
        if response['cod'] == str(200):
            day = 0
            embed = await self.createEmbed(response["list"][day], response["city"]["name"], response["city"]["country"], day)
            message = await ctx.send(embed=embed)
            await self.changeReactions(day, message, ctx)
            while(True):
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=360, check=lambda reaction, user: weatherCheck(reaction, user, day, message))
                except:
                    await message.delete()
                    break
                else:
                    if str(reaction) == "➡":
                        day += 1
                    elif str(reaction) == "⬅":
                        day -= 1
                    await message.edit(embed=await self.createEmbed(response["list"][day*8], response["city"]["name"], response["city"]["country"], day))
                    await self.changeReactions(day, message, ctx)
                    await message.remove_reaction(reaction, user)
        else:
            await ctx.send("The city your specified was not found.")