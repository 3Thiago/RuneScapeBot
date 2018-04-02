from csv import DictWriter
from discord import Member, File
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.owner_check import is_owner


class TicketCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command()
    async def tickets(self, ctx:Context, user:Member=None):
        '''
        Shows you all of the people who have tickets, and how many
        '''

        if user:
            user_id = user.id
        else:
            user_id = ctx.author.id

        async with self.bot.database() as db:
            data = await db('SELECT * FROM tickets WHERE user_id=$1', user_id)
        if data:
            i = data[0]
            ret = '**{}** has **{}** tickets.'.format(ctx.guild.get_member(i['user_id']), i['ticket_count'])
        else:
            ret = 'No tickets.'
        await ctx.send(ret)


    @command()
    @is_owner()
    async def cleartickets(self, ctx:Context):
        '''
        Removes all of the tickets from the database
        '''

        async with self.bot.database() as db:
            data = await db('DELETE FROM tickets')
        await ctx.send('Deleted all raffle tickets from the database.')


    @command()
    @is_owner()
    async def alltickets(self, ctx:Context):
        '''
        Removes all of the tickets from the database
        '''

        async with self.bot.database() as db:
            data = await db('SELECT user_id, ticket_count FROM tickets')
        with open('all_tickets.csv', 'w') as a:
            w = DictWriter(a, ['user_id', 'username', 'ticket_count'])
            w.writeheader()
            data = [{**i, 'username': str(self.bot.get_user(i['user_id']))} for i in data]
            w.writerows(data)
        await ctx.send(file=File('all_tickets.csv'))


def setup(bot:CustomBot):
    x = TicketCommands(bot)
    bot.add_cog(x)
