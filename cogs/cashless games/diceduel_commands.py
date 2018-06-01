from discord import Member
from discord.ext.commands import command, Context, MissingRequiredArgument, has_role
from cogs.utils.custom_bot import CustomBot
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.currency_checks import has_dice, has_set_currency
from cogs.utils.random_from_list import random_from_list


get_dice_roll = lambda x: random_from_list(x, [1, 2, 3, 4, 5, 6])
class Argument():
    def __init__(self, n):
        self.name = n


class DiceDuelCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command(aliases=['dd'])
    @has_dice()
    @has_role('Host')
    async def diceduel(self, ctx:Context, user:Member, user_two:str=None, amount:int=0):
        '''
        Runs a dice duel of one (against the host) or two users
        '''

        '''
        Possible invocation scenarios:
              |user*|user2|amount
            dd|@user|50   |
            dd|@user|@user|
            dd|@user|     |
            dd|@user|@user|50
        '''

        # Validate who's duelling who and for what
        if amount:
            user_one = user
            user_two = ctx.guild.get_member(int(''.join([i for i in user_two if i.isdigit()])))
        elif user_two:
            if user_two.isdigit():
                amount = int(user_two)
                user_one, user_two = ctx.author, user
            else:
                user_one = user
                user_two = ctx.guild.get_member(int(''.join([i for i in user_two if i.isdigit()])))
        else:
            user_one, user_two = ctx.author, user 

        # Get the dice of the two users
        user_one_dice = await self.bot.aget_die(user_one.id)
        user_two_dice = await self.bot.aget_die(user_two.id)

        # Roll their dice
        user_one_rolls = [user_one_dice.get_random() for i in range(2)]
        user_two_rolls = [user_two_dice.get_random() for i in range(2)]

        # Convert to dice
        user_one_diceroll = [get_dice_roll(i['result']) for i in user_one_rolls]
        user_two_diceroll = [get_dice_roll(i['result']) for i in user_two_rolls]
        
        # Embed it
        nonce_data = '{}\'s rolls: {}, {}\'s rolls: {}'.format(
            user_one.name,
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in user_one_rolls]),
            user_two.name,
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in user_two_rolls])
        )
        with CustomEmbed() as e:
            e.add_new_field(
                user_one.name + ' rolls', 
                '**{0}** ({1[0]} and {1[1]})'.format(sum(user_one_diceroll), user_one_diceroll)
            )
            e.add_new_field(
                user_two.name + ' rolls', 
                '**{0}** ({1[0]} and {1[1]})'.format(sum(user_two_diceroll), user_two_diceroll)
            )
            e.set_footer(text=nonce_data)

        # Check who won
        if sum(user_one_diceroll) == sum(user_two_diceroll):
            if [i for i in user_one.roles if i.name == 'Host']:
                winner = user_one
            else:
                winner = user_two
        else:
            winner = user_one if sum(user_one_diceroll) > sum(user_two_diceroll) else user_two
        text = 'The winner is {0.mention}!'.format(winner)
        await ctx.send(text, embed=e)

        # Store rolled dice
        async with self.bot.database() as db:
            await db.store_die(user_one_dice)
            await db.store_die(user_two_dice)


def setup(bot:CustomBot):
    x = DiceDuelCommands(bot)
    bot.add_cog(x)
