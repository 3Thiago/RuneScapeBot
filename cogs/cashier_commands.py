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
        validate_attempt = validate_currency(currency_type)
        if not validate_attempt:
            validate_attempt = validate_currency(amount)
            if not validate_attempt:
                await ctx.send('The specified currency type is not valid.')
                return
            else:
                amount, currency_type = currency_type, validate_currency(amount)
        else:
            currency_type = validate_attempt

        # Get the amount of money they want to modify by (int)
        amount = money_fetcher(amount)
        if not amount:
            await ctx.send('That value given for money could not be interpreted.')
            return

        # Modify the database
        async with self.bot.database() as db:
            await db.modify_user_currency(user, amount, currency_type)
            await db.log_user_mod(
                message=ctx.message, 
                cashier=ctx.author, 
                to=user, 
                amount=amount, 
                currency=currency_type, 
                reason='DEPOSIT'
                )
        await ctx.send("{.mention}'s account has been increased by `{}gp`.".format(user, amount))


    @command()
    async def withdraw(self, ctx:Context, user:Member, amount:str, currency_type:str):
        '''
        Lets you withdraw money form a specified user's account
        '''

        # Make sure they're specifying a valid currency type
        validate_attempt = validate_currency(currency_type)
        if not validate_attempt:
            validate_attempt = validate_currency(amount)
            if not validate_attempt:
                await ctx.send('The specified currency type is not valid.')
                return
            else:
                amount, currency_type = currency_type, validate_currency(amount)
        else:
            currency_type = validate_attempt

        # Get the amount of money they want to modify by (int)
        amount = money_fetcher(amount)
        if not amount:
            await ctx.send('That value given for money could not be interpreted.')
            return

        # Modify the database
        async with self.bot.database() as db:
            await db.modify_user_currency(user, -amount, currency_type)
            await db.log_user_mod(
                message=ctx.message, 
                cashier=ctx.author, 
                to=user, 
                amount=-amount, 
                currency=currency_type, 
                reason='WITHDRAWAL'
                )
        await ctx.send("{.mention}'s account has been decreased by `{}gp`.".format(user, amount))


def setup(bot:CustomBot):
    x = CashierCommands(bot)
    bot.add_cog(x)
