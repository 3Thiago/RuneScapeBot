from discord import Member
from discord.utils import get
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_errors import MissingRequiredRole
from cogs.utils.currency_validator import validate_currency
from cogs.utils.money_fetcher import money_fetcher


class MoneyCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command()
    async def transfer(self, ctx:Context, user:Member, amount:str, currency_type:str):
        '''
        Lets you transfer some of your own money to another user
        '''

        # Make sure they're specifying a valid currency type
        currency_type = validate_currency(currency_type)
        if not currency_type:
            await ctx.send('The specified currency type is not valid.')
            return

        # Get the amount of money they want to modify by (int)
        amount = money_fetcher(amount)

        # Modify the database
        async with self.bot.database() as db:
            await db.modify_user_currency(ctx.author, -amount, currency_type)
            await db.modify_user_currency(user, amount, currency_type)
        x = "{.mention}, you have successfully transferred `{}gp` to {.mention}.".format(ctx.author, amount, user)
        await ctx.send(x)


def setup(bot:CustomBot):
    x = MoneyCommands(bot)
    bot.add_cog(x)
