import discord

class GuildMember():
    def __init__(self, member):
        self.member = member

    def __str__(self):
        return str(self.member)

    def getMention(self):
        return self.member.mention

    def getEmbed(self):
        embed = discord.Embed(title=self.__str__())
        embed.set_thumbnail(url=str(self.member.avatar_url))
        roles = self.member.roles
        rolesStr = list(map(lambda role: str(role)+", ", roles))
        rolesStr[len(rolesStr)-1] = rolesStr[len(rolesStr)-1][:-2]
        embed.add_field(name="Roles", value="".join(rolesStr))
        return embed

class Player(GuildMember):
    def __init__(self, member):
        super().__init__(member)
        self.score = 0