from os import remove
from csv import DictWriter
from discord import File
from discord.ext.commands import command, Context, NotOwner
from cogs.utils.custom_bot import CustomBot
from cogs.utils.owner_check import predicate as is_owner


def database_to_csv(fp, data, *, extra_rows:list=[], update_function=None):
    w = DictWriter(fp, list(data[0].keys()) + extra_rows, lineterminator='\n')
    w.writeheader()
    data = [{**i} for i in data]
    if update_function:
        for i in data: 
            i.update(update_function(i))
    w.writerows([{i: str(o) for i, o in x.items()} for x in data])


class DatabaseCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    async def __local_check(self, ctx:Context):
        x = await is_owner(ctx)
        if x:
            return True
        raise NotOwner()


    @command()
    async def modlog(self, ctx:Context):
        '''
        Gives you the balance modifications for all of the users
        '''

        # Get relevant data
        async with self.bot.database() as db:
            data = await db('SELECT * FROM modification_log ORDER BY id DESC')
        filename = 'modification_log.csv'
        with open(filename, 'w', encoding='utf-8') as a: 
            database_to_csv(a, data)
        f = File(filename)
        await ctx.author.send(file=f)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        remove(filename)


    @command()
    async def cashlogs(self, ctx:Context):
        '''
        Gives you the balance modifications for the house
        '''

        # Get relevant data
        async with self.bot.database() as db:
            data = await db("SELECT * FROM modification_log WHERE reason='DEPOSIT' or reason='WITHDRAWAL' ORDER BY id DESC")
        filename = 'cash_log.csv'

        update_function = lambda i: {
            'cashier': str(self.bot.get_user(i['cashier_id'])), 
            'user':    str(self.bot.get_user(i['user_id'])) 
        }
        with open(filename, 'w', encoding='utf-8') as a: 
            database_to_csv(a, data, extra_rows=['cashier', 'user'], update_function=update_function)
        f = File(filename)
        await ctx.author.send(file=f)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        remove(filename)


    @command()
    async def housemodlog(self, ctx:Context):
        '''
        Gives you the balance modifications for the house
        '''

        # Get relevant data
        async with self.bot.database() as db:
            data = await db('SELECT * FROM house_modification_log ORDER BY id DESC')
        filename = 'house_modification_log.csv'
        with open(filename, 'w', encoding='utf-8') as a: 
            database_to_csv(a, data)
        f = File(filename)
        await ctx.author.send(file=f)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        remove(filename)



def setup(bot:CustomBot):
    x = DatabaseCommands(bot)
    bot.add_cog(x)
