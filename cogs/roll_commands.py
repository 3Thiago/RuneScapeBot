from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.money_fetcher import money_fetcher
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.currency_checks import has_dice, has_set_currency


class RollCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command(aliases=['roll', 'die'])
    @has_dice()
    @has_set_currency()
    async def dice(self, ctx:Context, segment:str=None, amount:str=None):
        '''
        Rolls a die for you
        '''

        # Get the user's currency
        async with self.bot.database() as db:
            currency_type = await db.get_user_currency_mode(ctx.author)

        # Check both amount and segment are defined
        if type(segment) == str and amount == None and money_fetcher(segment):
            amount = money_fetcher(segment)
            segment = 'HIGH'
        elif segment != None and amount == None:
            pass
        elif segment != None and amount != None:
            if segment[0].isnumeric():
                amount, segment = segment, amount
            amount = money_fetcher(amount)
        else:
            segment = 'HIGH'
            amount = None

        # Make sure the user has enough money to lose
        async with self.bot.database() as db:
            x = await db.get_user_currency(ctx.author, currency_type)
        if amount and amount * 2 > x:
            await ctx.send('You don\'t have enough money to make that bet.')
            return

        # See if segment is valid
        try:
            segment = {
                'high': 'HIGH', 'h': 'HIGH', 'hi': 'HIGH', 
                'middle': 'MID', 'mid': 'MID', 'medium': 'MID', 'm': 'MID',
                'low': 'LOW', 'l': 'LOW', 'bottom': 'LOW', 'bot': 'LOW'
            }[segment.lower()]
        except KeyError:
            await ctx.send('I can\'t work out what you\'re trying to bet on.')
            return
        segfunc = {
            'HIGH': lambda x: x >= 55 and x < 101,
            'MID': lambda x: x >= 45 and x < 55,
            'LOW': lambda x: x >= 0 and x < 45 
        }[segment]

        # Get and roll their die
        die = self.bot.get_die(ctx.author.id)
        provenfair = die.get_random()

        # See if they won or lost
        roll_result = provenfair['result']
        wonroll = segfunc(roll_result)

        # See how much to modify by
        if amount:
            modamount = 2 * amount if wonroll else -amount
            if segment == 'MID': modamount = 4 * amount

        # Generate an output for the user
        desc = '**{0.mention} has rolled a {1} on the percentile die and {2} the pot'.format(
            ctx.author,
            roll_result,
            {True: 'won', False: 'lost'}[wonroll]
            )
        if amount == None:
            desc += '**'
        else:
            desc += ' and `{}gp`**'.format(abs(modamount))

        # Store it in the database
        async with self.bot.database() as db:
            if amount:
                await db.modify_user_currency(ctx.author, modamount, currency_type)
            await db.store_die(die)

        # Send an embed with the data
        with CustomEmbed() as e:
            e.description = desc
            e.add_new_field('Nonce', provenfair['nonce'])
            e.add_new_field('Client Seed', provenfair['client_seed'])
            e.add_new_field('Server Seed Hash', provenfair['server_seed_hash'])
        await ctx.send(embed=e)


def setup(bot:CustomBot):
    x = RollCommands(bot)
    bot.add_cog(x)
