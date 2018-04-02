from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.money_fetcher import money_fetcher, money_displayer
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
            current_wallet = await db.get_user_currency(ctx.author, currency_type)
        if amount and amount > current_wallet:
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
            modamount = amount if wonroll else -amount
            if segment == 'MID' and wonroll: modamount = 3.5 * amount

        # See if they have any raffle tickets
        if str(currency_type) == 'oldscape': rafflemod = 4 * 10**6
        else: rafflemod = 25 * 10**6
        if amount: new_tickets = amount // rafflemod
        else: new_tickets = 0

        # Generate an output for the user
        desc = '**'
        if new_tickets:
            desc += 'Along with their {0} new raffle tickets, '.format(new_tickets)
        desc += '{0.mention} has rolled a {1} on the percentile die and {2} the pot'.format(
            ctx.author,
            roll_result,
            {True: 'won', False: 'lost'}[wonroll]
            )
        if amount and modamount > 0: 
            desc += ' of {}**'.format(money_displayer(modamount + amount))
        else: desc += '**'

        # Store it in the database
        async with self.bot.database() as db:
            if amount:
                await db.modify_user_currency(ctx.author, modamount, currency_type)
                await db.log_user_mod(
                    message=ctx.message, 
                    to=ctx.author, 
                    amount=modamount, 
                    currency=currency_type, 
                    reason='ROLL'
                    )
            if new_tickets:
                await db.add_tickets_for_user(ctx.author, new_tickets)
            await db.store_die(die)

        # Send an embed with the data
        with CustomEmbed() as e:
            e.description = desc
            e.set_thumbnail(url='https://vignette.wikia.nocookie.net/runescape2/images/f/f2/Dice_bag_detail.png/revision/latest/scale-to-width-down/100?cb=20111120013858')
            e.set_footer(text='Nonce: {}'.format(provenfair['nonce']) + '. To see all random stats, run the mydice command.')
        await ctx.send(embed=e)


def setup(bot:CustomBot):
    x = RollCommands(bot)
    bot.add_cog(x)
