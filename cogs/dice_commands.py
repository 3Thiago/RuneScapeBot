from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.provably_fair import ProvablyFair
from cogs.utils.custom_embed import CustomEmbed


class DiceCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command(aliases=['newdie'])
    async def newdice(self, ctx:Context, seed:str=None):
        '''
        Creates a new set of dice for you to use
        '''

        d = self.bot.get_die(ctx.author.id)
        if d != None and d.valid:
            await ctx.send('You already have a die generated.')
            return

        # Make the dice
        die = ProvablyFair(user_id=ctx.author.id, client_seed=seed)

        # Cache and database it
        self.bot.set_die(ctx.author.id, die)
        async with self.bot.database() as db: 
            await db.store_die(die)

        # Print out to user
        x = 'Your new die has been created - your server seed hash is `{.server_seed_hash}`.'.format(die)
        await ctx.send(x)


    @command()
    async def setseed(self, ctx:Context, seed:str):
        '''
        Allows you to set the seed for your dice
        '''
        d = self.bot.get_die(ctx.author.id)
        if d != None and d.valid:
            await ctx.send('You can\'t change your seed partway through your dice\'s use. To set a custom seed, invalidate your current one with the `serverseed` command, then make a new one with `newdice {}`.'.format(seed))
            return

        # Make the dice
        die = ProvablyFair(user_id=ctx.author.id, client_seed=seed)

        # Cache and database it
        self.bot.set_die(ctx.author.id, die)
        async with self.bot.database() as db: 
            await db.store_die(die)

        # Print out to user
        x = 'Your new die has been created - your server seed hash is `{.server_seed_hash}`.'.format(die)
        await ctx.send(x)


    @command()
    async def serverseed(self, ctx:Context):
        '''
        Gets the unhashed server seed and invalidates your current dice
        '''

        d = self.bot.get_die(ctx.author.id)
        if d == None or d.valid == False:
            await ctx.send('You don\'t have a valid dice to get the seed of.')
            return

        d.valid = False
        async with self.bot.database() as db:
            sql = 'DELETE FROM dice WHERE user_id=$1'
            await db(sql, ctx.author.id)

        url = 'https://dicesites.com/primedice/verifier?'
        params = {
            'ss': d.server_seed,
            'ssh': d.server_seed_hash,
            'cs': d.client_seed,
            'ln': d.nonce
        }
        url = url + '&'.join(['{}={}'.format(i, o) for i, o in params.items()])
        with CustomEmbed() as e:
            e.set_author(name='Click Here', url=url)
        await ctx.send(
            'Your server seed is `{0.server_seed}`, hash is `{0.server_seed_hash}`, and your client seed is `{0.client_seed}`. Your die has now been invalidated.'.format(d),
            embed=e
            )


def setup(bot:CustomBot):
    x = DiceCommands(bot)
    bot.add_cog(x)
