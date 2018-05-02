from asyncio import TimeoutError
from discord import Member
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.random_from_list import random_from_list
from cogs.utils.custom_errors import NoDiceGenerated


def random_card(roll:float):
    return random_from_list(roll, [
        'Ace', 'Two', 'Three', 'Four',
        'Five', 'Six', 'Seven', 'Eight', 'Nine',
        'Ten', 'Jack', 'Queen', 'King']
        )


class Game(object):

    def __init__(self, dealer:int, bettor:int):
        self.message = None
        self.embed = None
        self.dealer = dealer 
        self.bettor = bettor
        self.dealer_hand = []
        self.bettor_hand = []
        self.dealer_turn = False

    def display(self):
        if self.dealer_turn == False:
            return [
                ', '.join(self.bettor_hand),
                ', '.join([self.dealer_hand[0], 'Unknown'])
            ]
        return [', '.join(self.bettor_hand), ', '.join(self.dealer_hand)]


class BlackjackCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot
        self.running_games = {}  # Dealer, Game


    @command(hidden=True)
    async def bj(self, ctx:Context, user:Member):
        '''
        Gives you a fake game of blackjack to play
        '''

        if ctx.author.id != 141231597155385344:  # Temp for testing
            return

        # Make sure they don't accidentally abandon their current match
        if ctx.author.id in self.running_games:
            x = await ctx.send('Doing this will erase the game you\'re already in. Do you want to continue?')
            for i in ['\N{THUMBS DOWN SIGN}', '\N{THUMBS UP SIGN}']: await x.add_reaction(i)
            check = lambda r, u: u.id == ctx.author.id and str(r.emoji) in ['\N{THUMBS DOWN SIGN}', '\N{THUMBS UP SIGN}']
            try:
                r, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except TimeoutError:
                await x.delete()
                return
            if str(r.emoji) == '\N{THUMBS DOWN SIGN}':
                await x.delete()
                await ctx.send('Alright, abandoning game creation.')
                return
            await x.delete()

        # Make a new game object for them to use
        self.running_games[ctx.author.id] = game =  Game(ctx.author.id, user.id)

        # Get the user some cards
        user_dice = self.bot.get_die(user.id)
        if user_dice == None:
            raise NoDiceGenerated()
        user_random = [user_dice.get_random() for i in range(2)]
        game.bettor_hand = [random_card(i['result']) for i in user_random]

        # Get the dealer some cards
        dealer_dice = self.bot.get_die(ctx.author.id)
        if user_dice == None:
            raise NoDiceGenerated()
        dealer_random = [dealer_dice.get_random() for i in range(2)]
        game.dealer_hand = [random_card(i['result']) for i in dealer_random]

        # Show them it's random
        nonce_data = 'User nonces: [{}], dealer nonces: [{}]'.format(
            ', '.join([str(i['nonce']) for i in user_random]),
            ', '.join([str(i['nonce']) for i in dealer_random])
            )

        # Set up the embed
        display = game.display()
        with CustomEmbed() as e:
            e.set_author_to_user(ctx.author, use_user_colour=False, image_to=None)
            e.description = 'Use the `hit` or `stand` commands to continue, {}'.format(user.mention)
            e.add_new_field('Your Hand', display[0])
            e.add_new_field('House Hand', display[1])
            e.set_footer(text=nonce_data)
        game.embed = e

        # Display to userman
        m = await ctx.send(embed=e)
        game.message = m


def setup(bot:CustomBot):
    x = BlackjackCommands(bot)
    bot.add_cog(x)
