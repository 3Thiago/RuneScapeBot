from discord import Member
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.money_fetcher import money_displayer
from cogs.utils.currency_checks import has_dice
from cogs.utils.random_from_list import random_from_list


class HotColdCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot
        self.can_roll = []
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
    async def hotcold(self, ctx:Context, user:Member, amount:int=0):
        '''
        Runs the hot/cold bet for you
        '''

        self.can_roll.append(user.id)
        await ctx.send('{.mention}, use the `hot`, `cold`, or `rainbow` commands to make your bet.'.format(user))


    async def roll_dice(self, ctx:Context, prediction:str):
        '''
        Rolls a dice, betting for a particular segment
        '''

        # Get their die
        die = self.bot.get_die(ctx.author.id)
        roll = die.get_random()

        # The "who won" functions
        segfunc = {
            'HOT': lambda x: x in ['RED', 'ORANGE', 'YELLOW'],
            'COLD': lambda x: x in ['BLUE', 'PASTEL', 'PURPLE'],
            'RAINBOW': lambda x: x in ['RAINBOW'] 
        }.get(prediction, lambda x: x == prediction)
        all_colours = ['RED', 'ORANGE', 'YELLOW', 'BLUE', 'PASTEL', 'PURPLE', 'RAINBOW'] 
        rolled_flower = random_from_list(roll['result'], all_colours)
        won_bool = segfunc(rolled_flower)  # Boolean, whether or not they won

        # Outputs
        desc = 'You picked **{0}** and {1} the pot.'.format(
            rolled_flower.lower(),
            {True:'won',False:'lost'}.get(won_bool)
        )
        with CustomEmbed() as e:
            e.description = desc
            e.set_thumbnail(url=self.flower_colours.get(rolled_flower))
            e.set_footer(text='Roll: {}; Nonce: {}'.format(roll['result'], roll['nonce']))
        await ctx.send(embed=e)
        async with self.bot.database() as db:
            await db.store_die(die)


    @command(hidden=True, aliases=['h'])
    @has_dice()
    async def hot(self, ctx:Context):
        '''
        Bet functions for the hotcold command
        '''

        if ctx.author.id not in self.can_roll:
            return
        self.can_roll.remove(ctx.author.id)
        await self.roll_dice(ctx, 'HOT')


    @command(hidden=True, aliases=['c'])
    @has_dice()
    async def cold(self, ctx:Context):
        '''
        Bet functions for the hotcold command
        '''

        if ctx.author.id not in self.can_roll:
            return
        self.can_roll.remove(ctx.author.id)
        await self.roll_dice(ctx, 'COLD')


    @command(hidden=True, aliases=['r'])
    @has_dice()
    async def rainbow(self, ctx:Context):
        '''
        Bet functions for the hotcold command
        '''

        if ctx.author.id not in self.can_roll:
            return
        self.can_roll.remove(ctx.author.id)
        await self.roll_dice(ctx, 'RAINBOW')


def setup(bot:CustomBot):
    x = HotColdCommands(bot)
    bot.add_cog(x)
