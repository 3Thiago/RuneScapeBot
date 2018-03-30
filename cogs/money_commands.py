from discord import Member
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.currency_validator import validate_currency
from cogs.utils.money_fetcher import money_fetcher, money_displayer
from cogs.utils.currency_checks import has_set_currency


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

        # Make sure they don't send off their money to bots
        if user.bot:
            await ctx.send('That user is a bot. Why are you like this.')
            return

        # Get the amount of money they want to modify by (int)
        amount = money_fetcher(amount)

        # Modify the database
        async with self.bot.database() as db:
            await db.modify_user_currency(ctx.author, -amount, currency_type)
            await db.modify_user_currency(user, amount, currency_type)
            await db.log_user_mod(ctx.message, ctx.author, user, modamount, currency_type)
        x = "{.mention}, you have successfully transferred `{}gp` to {.mention}.".format(ctx.author, amount, user)
        await ctx.send(x)


    @command()
    async def setmode(self, ctx:Context, currency_type:str):
        '''
        Set the currency you use in your betting sessions
        '''

        # Make sure they're specifying a valid currency type
        currency_type = validate_currency(currency_type)
        if not currency_type:
            await ctx.send('The specified currency type is not valid.')
            return

        async with self.bot.database() as db:
            await db.set_user_currency_mode(ctx.author, currency_type)
        await ctx.send('Your currency mode has been updated.')


    @command(aliases=['wallet'])
    async def balance(self, ctx:Context):
        '''
        Gives you your current balance
        '''

        async with self.bot.database() as db:
            x = await db('SELECT * FROM user_data WHERE user_id=$1', ctx.author.id)
        with CustomEmbed() as e:
            e.add_new_field('RS3', money_displayer(x[0]['newscape']))
            e.add_new_field('07scape', money_displayer(x[0]['oldscape']))
        await ctx.author.send(embed=e)
        await ctx.message.add_reaction('\N{ENVELOPE WITH DOWNWARDS ARROW ABOVE}')


def setup(bot:CustomBot):
    x = MoneyCommands(bot)
    bot.add_cog(x)
