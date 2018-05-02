from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot


class COGNAMEWEW(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


def setup(bot:CustomBot):
    x = COGNAMEWEW(bot)
    bot.add_cog(x)
