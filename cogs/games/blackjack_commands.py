from asyncio import TimeoutError
from discord import Member
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.random_from_list import random_from_list
from cogs.utils.custom_errors import NoDiceGenerated
from cogs.utils.cards import CARD_CLUBS
from cogs.utils.blackjack_game import Game


def random_card(roll:float):
    return random_from_list(roll, CARD_CLUBS)


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
        if game.is_bust:
            if game.dealer_turn:
                await self.switch_blackjack_turn(ctx)
            else:
                await self.end_blackjack_game(ctx)
            return
        if game.is_21:
            await self.switch_blackjack_turn(ctx)
            return

        # Edit display
        # await game.message.edit(embed=game.embed)
        await ctx.send(embed=game.embed)


    async def switch_blackjack_turn(self, ctx:Context):
        '''
        Switches the turns - does what stand would do but can be called by other methods too
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
            # await game.message.edit(content='Game of <@{}> and <@{}> is completed.'.format(game.bettor, game.dealer), embed=e)
            await ctx.send('Game of <@{}> and <@{}> is completed.'.format(game.bettor, game.dealer), embed=e)


        # Switch players
        else:
            game.dealer_turn = True
            # await game.message.edit(content='It is now <@{}>\'s turn.'.format(game.dealer), embed=game.embed)
            await ctx.send('It is now <@{}>\'s turn.'.format(game.dealer), embed=game.embed)


    async def end_blackjack_game(self, ctx:Context):
        '''
        Ends any given blackjack game
        '''

        try:
            game, role = Game.get_game(ctx.author.id)
        except ValueError as e:
            return

        try: del Game.running_games[game.dealer]
        except KeyError as e: pass
        try: del Game.running_games[game.bettor]
        except KeyError as e: pass

        e = game.embed
        e.description = ''
        await ctx.send('Game of <@{}> and <@{}> is completed.'.format(game.bettor, game.dealer), embed=e)


    @command(hidden=True)
    async def stand(self, ctx:Context):
        '''
        Stands so you can't draw any more cards from the blackjack deck
        '''

        await self.switch_blackjack_turn(ctx)


def setup(bot:CustomBot):
    x = BlackjackCommands(bot)
    bot.add_cog(x)
