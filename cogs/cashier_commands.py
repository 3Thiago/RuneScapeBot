from discord import Member
from discord.utils import get
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_errors import MissingRequiredRole
from cogs.utils.currency_validator import validate_currency
from cogs.utils.money_fetcher import money_fetcher


class CashierCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    async def __local_check(self, ctx:Context):
        x = get(ctx.author.roles, name='Cashier')
        y = await self.bot.is_owner(ctx.author)
        if x or y: return True
        else: raise MissingRequiredRole('Cashier')


    @command()
    async def deposit(self, ctx:Context, user:Member, amount:str, currency_type:str):
        '''
        Allows you to deposit money into a specified user's account
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
            await db.modify_user_currency(user, amount, currency_type)
        await ctx.send('Database modified.')


    @command()
    async def withdraw(self, ctx:Context, user:Member, amount:str, currency_type:str):
        '''
        Lets you withdraw money form a specified user's account
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
            await db.modify_user_currency(user, -amount, currency_type)
        await ctx.send('Database modified.')


def setup(bot:CustomBot):
    x = CashierCommands(bot)
    bot.add_cog(x)
