import datetime
import discord
from discord.ext import commands
from log import log
import utils

class Chess(commands.Cog):
    def __init__(self, client):
        self.client = client
        log(1, "Chess cog loaded.")

    def _getGameDesc(self, user, opponent):
        result = user["result"]
        if result == "win":
            return f"Won against {opponent['username']}."
        if result == "checkmated":
            return f"Checkmated by {opponent['username']}."
        if result == "agreed":
            return f"Agreed on draw with {opponent['username']}."
        if result == "repetition":
            return f"The user and {opponent['username']} repeated moves, which resulted in a tie."
        if result == "timeout":
            return f"The game timed-out. User played against {opponent['username']}."
        if result == "resigned":
            return f"The user resigned. Played against {opponent['username']}."
        if result == "resigned":
            return f"The game resulted in a stalemate. User played against {opponent['username']}."
        if result == "lose":
            return f"Lost to {opponent['username']}."
        if result == "abandoned":
            return f"The game was abandoned. User played against {opponent['username']}."

    def _getgameembed(self, games, profile):
        if 'name' in profile.keys():
            name = profile['name']
        else:
            name = profile['username']
        embed = discord.Embed(title=f"Last 5 games or less played by {name}", url=profile["url"], color=discord.Colour.dark_green())
        resultStr = ""
        games.reverse()
        for i, game in enumerate(games):
            if i > 4:
                break
            if game["white"]["username"].lower() == profile['username']:
                player = game["white"]
                against = game["black"]
            else:
                player = game["black"]
                against = game["white"]
            resultStr += f"**{i+1}. {self._getGameDesc(player, against)}** \n[Go To Game]({game['url']}) \nDate: {datetime.datetime.fromtimestamp(game['end_time']).strftime('%Y-%m-%d')}\n"
        embed.add_field(name=":game_die: List of Matches", value=resultStr, inline=True)
        embed.set_image(url="https://i.ibb.co/NWqYLNf/1-j8ihw-CTi-Wsf92-Bbemg8-Vn-A.png")
        embed.set_footer(text="All data is provided by the Chess.com API")
        return embed

    def _getembed(self, result, stats, name):
        embed = discord.Embed(title=name, url=result["url"], color=discord.Colour.dark_green())
        dt_obj = datetime.datetime.fromtimestamp(result["joined"])
        embed.add_field(name="Joined at", value=dt_obj.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        try:
            embed.set_thumbnail(url=result["avatar"])
        except:
            embed.set_thumbnail(url="https://i.ibb.co/wCTWJgP/empty-avatar.png")
        rapid = stats["chess_rapid"]
        embed.add_field(name="Current Rating", value=rapid["last"]['rating'], inline=True)
        embed.add_field(name="Best Rating", value=rapid["best"]['rating'], inline=True)
        embed.add_field(name="Wins", value=rapid["record"]["win"], inline=True)
        embed.add_field(name="Losses", value=rapid["record"]["loss"], inline=True)
        if rapid["record"]["draw"] > 0:
            embed.add_field(name="Draws", value=rapid["record"]["draw"], inline=True)
        embed.add_field(name="Best Game", value=f"[Go To Game]({rapid['best']['game']})", inline=True)
        embed.set_footer(text="All data is provided by the Chess.com API")
        return embed

    @commands.command(aliases=["ChessInfo"])
    async def chess(self, ctx, *args):
        if args is not None and len(args) == 2:
            if args[0] == "find":
                # result = requests.get(f"https://api.chess.com/pub/player/{args[1]}")
                # result = result.json()
                result = await utils.requestJSON(f"https://api.chess.com/pub/player/{args[1]}", 'get')
                if "username" in result.keys():
                    # stats = requests.get(f"https://api.chess.com/pub/player/{args[1]}/stats")
                    # stats = stats.json()
                    stats = await utils.requestJSON(f"https://api.chess.com/pub/player/{args[1]}/stats", 'get')
                    await ctx.send(embed=self._getembed(result, stats, args[1]))
                else:
                    await ctx.send("Could not find the player you were searching for. Please make sure you typed the correct username.")
            if args[0] == "games":
                # result = requests.get(f"https://api.chess.com/pub/player/{args[1]}")
                # result = result.json()
                result = await utils.requestJSON(f"https://api.chess.com/pub/player/{args[1]}", 'get')
                if "username" in result.keys():
                    # games = requests.get(f"https://api.chess.com/pub/player/{args[1]}/games/{datetime.date.today().year}/{datetime.date.today().month}")
                    # games = games.json()
                    month = str(datetime.date.today().month)
                    if len(month) == 1:
                        month = "0"+month
                    games = await utils.requestJSON(f"https://api.chess.com/pub/player/{args[1]}/games/{datetime.date.today().year}/{month}", 'get')
                    try:
                        games = games["games"]
                    except:
                        await ctx.send("The Chess.com API is not responding. Please try again later.")
                    else:
                        if len(games) == 0:
                            await ctx.send("The player you requested didn't play any games this month yet.")
                        else:
                            await ctx.send(embed=self._getgameembed(games, result))
                else:
                    await ctx.send("Could not find the player you were searching for. Please make sure you typed the correct username.")