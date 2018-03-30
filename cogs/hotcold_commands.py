from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.money_fetcher import money_fetcher, money_displayer
from cogs.utils.currency_checks import has_dice, has_set_currency


class HotColdCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot
        self.flower_colours = {
          "ORANGE": "https://vignette1.wikia.nocookie.net/runescape2/images/9/99/Orange_flowers_detail.png/revision/latest?cb=20160918221429",
          "RED": "https://vignette4.wikia.nocookie.net/runescape2/images/6/6c/Red_flowers_detail.png/revision/latest?cb=20160918221431",
          "YELLOW": "https://vignette.wikia.nocookie.net/runescape2/images/a/a6/Yellow_flowers_detail.png/revision/latest?cb=20160918221432",
          "BLUE": "https://vignette4.wikia.nocookie.net/runescape2/images/d/d6/Blue_flowers_detail.png/revision/latest?cb=20160918221426",
          "PASTEL": "https://vignette3.wikia.nocookie.net/runescape2/images/5/55/Flowers_%28pastel%29_detail.png/revision/latest?cb=20160918221429",
          "PURPLE": "https://vignette3.wikia.nocookie.net/runescape2/images/3/3d/Purple_flowers_detail.png/revision/latest?cb=20160918221430",
          "RAINBOW": "https://vignette2.wikia.nocookie.net/runescape2/images/f/fd/Flowers_%28mixed%29_detail.png/revision/latest?cb=20160918221426"
        }


    @command(aliases=['hc'])
    @has_dice()
    @has_set_currency()
    async def hotcold(self, ctx:Context, prediction:str, amount:str=None):
        '''
        Runs the hot/cold bet for you
        '''

        # Get the user's currency
        async with self.bot.database() as db:
            currency_type = await db.get_user_currency_mode(ctx.author)

        # Check both amount and prediction are defined
        if amount == None and money_fetcher(prediction):
            await ctx.send('You need to specify what you\'re betting on.')
            return
        elif prediction != None and amount != None:
            if prediction[0].isnumeric():
                amount, prediction = prediction, amount
            amount = money_fetcher(amount)

        # Make sure the user has enough money to lose
        async with self.bot.database() as db:
            current_wallet = await db.get_user_currency(ctx.author, currency_type)
        if amount and amount > current_wallet:
            await ctx.send('You don\'t have enough money to make that bet.')
            return

        # See if the prediction is valid
        try:
            prediction = {
                'h': 'HOT', 'hot': 'HOT', 'warm': 'HOT',
                'c': 'COLD', 'cold': 'COLD', 'col': 'COLD',
                'r': 'RAINBOW', 'rainbow': 'RAINBOW', 'rain': 'RAINBOW', 'rb': 'RAINBOW'
            }[prediction.lower()]
        except KeyError:
            await ctx.send('I can\'t work out what you\'re trying to bet on.')
            return

        # Generate the functions to get validity
        segfunc = {
            'HOT': lambda x: x in ['RED', 'ORANGE', 'YELLOW'],
            'COLD': lambda x: x in ['BLUE', 'PASTEL', 'PURPLE'],
            'RAINBOW': lambda x: x in ['RAINBOW'] 
        }[prediction]

        # Set all of the colours
        all_colours = ['RED', 'ORANGE', 'YELLOW', 'BLUE', 'PASTEL', 'PURPLE', 'RAINBOW'] 

        # Get and roll their die
        die = self.bot.get_die(ctx.author.id)
        provenfair = die.get_random()

        # See if they won or lost
        roll_result = provenfair['result']
        roll_calc = [i for i in range(1, 8) if roll_result >= (100*i)/7]
        rolled_colour = all_colours[len(roll_calc)]
        wonroll = segfunc(rolled_colour)

        # See how much to modify by
        if amount:
            modamount = 2 * amount if wonroll else -amount
            if prediction == 'RAINBOW' and wonroll: modamount = 4 * amount

        # Generate an output for the user
        desc = '**{0.mention} has picked {1} and {2} the pot'.format(
            ctx.author,
            rolled_colour.lower(),
            {True: 'won', False: 'lost'}[wonroll]
            )
        if amount: desc += ' of {}**'.format(money_displayer(abs(modamount)))
        else: desc += '**'

        # Store it in the database
        async with self.bot.database() as db:
            if amount:
                await db.modify_user_currency(ctx.author, modamount, currency_type)
                await db.log_user_mod(ctx.message, None, ctx.author, modamount, currency_type)
            await db.store_die(die)

        # Send an embed with the data
        with CustomEmbed() as e:
            e.description = desc
            e.set_thumbnail(url=self.flower_colours.get(rolled_colour))
            e.set_footer(text='Roll: {}; Nonce: {}'.format(provenfair['result'], provenfair['nonce']) + '. To see all random stats, run the mydice command.')
        await ctx.send(embed=e)


def setup(bot:CustomBot):
    x = HotColdCommands(bot)
    bot.add_cog(x)
