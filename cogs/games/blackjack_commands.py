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

    running_games = {
    }  # user, Game

    def __init__(self, dealer:int, bettor:int):
        # For editing later
        self.message = None

        # Who's playing
        self.dealer = dealer 
        self.bettor = bettor

        # Randomness data
        self.bettor_random = None
        self.dealer_random = None

        # Game data
        self.dealer_hand = []
        self.bettor_hand = []
        self.dealer_turn = False

        # Random data

        # Make it easier on myself to grab games
        self.running_games[dealer] = (self, 'dealer')
        self.running_games[bettor] = (self, 'bettor')

    @classmethod
    def get_game(cls, user_id:int):
        return cls.running_games.get(user_id)

    @property
    def embed(self):

        nonce_data = 'Bettor nonces: [{}], dealer nonces: [{}]'.format(
            ', '.join([str(i['nonce']) for i in self.bettor_random]),
            ', '.join([str(i['nonce']) for i in self.dealer_random])
            )

        if self.dealer_turn == False:
            display = [
                ', '.join(self.bettor_hand),
                ', '.join([self.dealer_hand[0], 'Unknown'])
            ]
        else:
            display = [', '.join(self.bettor_hand), ', '.join(self.dealer_hand)]

        user = {True: self.dealer, False: self.bettor}[self.dealer_turn]
        role = {True: 'dealer', False: 'bettor'}[self.dealer_turn]

        with CustomEmbed(colour=0x325c95) as e:
            e.description = 'Use the `hit` or `stand` commands to continue, <@{}> ({})'.format(user, role)
            e.add_new_field('Bettor Hand', display[0])
            e.add_new_field('House Hand', display[1])
            e.set_footer(text=nonce_data)
        return e


class BlackjackCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot
        self.running_games = [] 


    @command(hidden=True)
    async def bj(self, ctx:Context, user:Member):
        '''
        Gives you a nice fake game of blackjack to play
        '''

        if ctx.author.id == user.id or user.bot:
            await ctx.send('Are you serious .-.')
            return

        # Make a new game object for them to use
        game = Game(ctx.author.id, user.id)
        # self.running_games.append(game)

        # Get the user some cards
        user_die = self.bot.get_die(user.id)
        if user_die == None:
            raise NoDiceGenerated()
        user_random = [user_die.get_random() for i in range(2)]
        game.bettor_hand = [random_card(i['result']) for i in user_random]

        # Get the dealer some cards
        dealer_die = self.bot.get_die(ctx.author.id)
        if dealer_die == None:
            raise NoDiceGenerated()
        dealer_random = [dealer_die.get_random() for i in range(2)]
        game.dealer_hand = [random_card(i['result']) for i in dealer_random]

        # Store the randomness data
        game.bettor_random = user_random
        game.dealer_random = dealer_random

        # Display to userman
        m = await ctx.send('It is now <@{}>\'s turn.'.format(game.bettor), embed=game.embed)
        game.message = m


    @command(hidden=True)
    async def hit(self, ctx:Context):
        '''
        Hits you with your best shot, fires away
        '''

        try:
            game, role = Game.get_game(ctx.author.id)
        except ValueError as e:
            return

        # Make sure the right person is playing
        if game.dealer == game.bettor:
            pass
        elif game.dealer_turn and game.dealer != ctx.author.id:
            return
        elif game.dealer_turn == False and game.bettor != ctx.author.id:
            return

        # Generate random
        user_die = self.bot.get_die(ctx.author.id)
        if user_die == None:
            raise NoDiceGenerated()
        user_random = user_die.get_random()

        # Get random card
        getattr(game, '{}_hand'.format(role)).append(random_card(user_random['result']))
        getattr(game, '{}_random'.format(role)).append(user_random)

        # Edit display
        await game.message.edit(embed=game.embed)
        try:
            await ctx.message.delete()
        except Exception as e:
            await ctx.message.add_reaction('\N{OK HAND SIGN}')


    @command(hidden=True)
    async def stand(self, ctx:Context):
        '''
        Stands so you can't draw any more cards from the blackjack deck
        '''

        try:
            game, role = Game.get_game(ctx.author.id)
        except ValueError as e:
            return

        # Make sure the right person is playing
        if game.dealer == game.bettor:
            pass
        elif game.dealer_turn and game.dealer != ctx.author.id:
            return
        elif game.dealer_turn == False and game.bettor != ctx.author.id:
            return

        # See if you need to stop the game
        if role == 'dealer': 
            try: del Game.running_games[game.dealer]
            except KeyError as e: pass
            try: del Game.running_games[game.bettor]
            except KeyError as e: pass

            e = game.embed
            e.description = ''
            await game.message.edit(content='Game of <@{}> and <@{}> completed.'.format(game.bettor, game.dealer), embed=e)

        # Switch players
        else:
            game.dealer_turn = True
            await game.message.edit(content='It is now <@{}>\'s turn.'.format(game.dealer), embed=game.embed)

        try:
            await ctx.message.delete()
        except Exception as e:
            await ctx.message.add_reaction('\N{OK HAND SIGN}')


def setup(bot:CustomBot):
    x = BlackjackCommands(bot)
    bot.add_cog(x)
