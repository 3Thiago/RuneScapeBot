from os import remove
from csv import DictWriter
from discord import Member, File
from discord.ext.commands import command, Context, has_role
from cogs.utils.custom_bot import CustomBot
from cogs.utils.owner_check import is_owner


class TicketGetter(object):

    counter = 0

    @classmethod
    def get(cls, amount):
        start = cls.counter + 1
        cls.counter += amount
        end = cls.counter
        if start == end:
            return start
        return '{} - {}'.format(start, end)


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

        # Get relevant data
        async with self.bot.database() as db:
            data = await db('SELECT user_id, ticket_count FROM tickets')

        # Save it to a CSV file
        with open('all_tickets.csv', 'w') as a:
            w = DictWriter(a, ['user_id', 'username', 'ticket_count', 'ticket_numbers'])
            w.writeheader()
            data = [{**i, 'username': str(self.bot.get_user(i['user_id'])), 'ticket_numbers': TicketGetter.get(i['ticket_count'])} for i in data]
            w.writerows(data)
        TicketGetter.counter = 0
        
        await ctx.author.send(file=File('all_tickets.csv'))
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

        # Remove the file after sending it
        remove('all_tickets.csv')


    @command()
    @has_role("Host")
    async def addtickets(self, ctx:Context, user:Member, amount:int):
        '''
        Adds a number of tickets to a user
        '''

        # Modify database
        async with self.bot.database() as db:
            try:
                await db('INSERT INTO tickets VALUES ($1, $2)', user.id, amount)
            except Exception:
                await db('UPDATE tickets SET ticket_count=ticket_count+$1 WHERE user_id=$2', amount, user.id)

        # Return to user
        await ctx.send("Ticket count for **{!s}** has been updated.".format(user))


    @command(aliases=['deletetickets'])
    @has_role("Host")
    async def removetickets(self, ctx:Context, user:Member, amount:int):
        '''
        Adds a number of tickets to a user
        '''

        # Modify database
        async with self.bot.database() as db:
            try:
                await db('UPDATE tickets SET ticket_count=ticket_count-$1 WHERE user_id=$2', amount, user.id)
                t = await db('SELECT ticket_count FROM tickets WHERE user_id=$1', user.id)
                if t[0]['ticket_count'] <= 0:
                    await db('DELETE FROM tickets WHERE user_id=$1', user.id)
            except Exception:
                await ctx.send('That user has no tickets already.')
                return

        # Return to user
        await ctx.send("Ticket count for **{!s}** has been updated.".format(user))


def setup(bot:CustomBot):
    x = TicketCommands(bot)
    bot.add_cog(x)
