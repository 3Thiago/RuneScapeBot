from datetime import datetime as dt
from discord import Message
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.owner_check import is_owner


class GiveawayCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command()
    @is_owner()
    async def giveaway(self, ctx:Context):
        '''
        Triggers the giveaway for you
        '''

        self.bot.giveaway.lastrun = dt(year=2000, month=1, day=1)
        await ctx.send('The giveaway has been triggered - it will run within the next minute.')


    async def on_message(self, message:Message):
        '''
        Used to count users who send messages into the correct channel
        '''

        if self.bot.giveaway.running:
            if message.author.bot == False and message.channel.id == self.bot.giveaway.channel_id:
                i = message.author.id
                if i in self.bot.giveaway.counted:
                    pass
                else:
                    self.bot.giveaway.counted.add(message.author.id)
                    await message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot:CustomBot):
    x = GiveawayCommands(bot)
    bot.add_cog(x)


