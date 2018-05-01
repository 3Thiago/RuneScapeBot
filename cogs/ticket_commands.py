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
            data = await db('SELECT * FROM tickets WHERE user_id=$1 AND day>$2-7 ORDER BY day DESC', user_id, self.bot.get_current_day_number())
        if not data:
            await ctx.send('No tickets.')
            return

        # Counter to sum up this week's tickets
        total = 0

        # Get today data
        current_day_number = self.bot.get_current_day_number()

        # See if they have anything today
        today = data[0]
        if today['day'] == current_day_number:
            ticket_count = today['ticket_count']
        else:
            ticket_count = 0
        plural = '' if ticket_count == 1 else 's'
        ret = '**Today:** {} ticket{}\n'.format(ticket_count, plural)

        # Add in the week's data
        for i in data:
            total += i['ticket_count']
        plural = '' if total == 1 else 's'
        ret +='**This week:** {} ticket{}\n'.format(total, plural)

        # Send to user
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
        with open('all_tickets.csv', 'w', encoding='utf-8') as a:
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
                await db('INSERT INTO tickets VALUES ($1, $2, $3)', user.id, amount, self.bot.get_current_day_number())
            except Exception:
                await db('UPDATE tickets SET ticket_count=ticket_count+$1 WHERE user_id=$2 AND day=$3', amount, user.id, self.bot.get_current_day_number())

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
                await db('UPDATE tickets SET ticket_count=ticket_count-$1 WHERE user_id=$2 AND day=$3', amount, user.id, self.bot.get_current_day_number())
                t = await db('SELECT ticket_count FROM tickets WHERE user_id=$1 AND day=$2', user.id, self.bot.get_current_day_number())
                if t[0]['ticket_count'] <= 0:
                    await db('DELETE FROM tickets WHERE user_id=$1 AND day=$2', user.id, self.bot.get_current_day_number())
            except Exception:
                await ctx.send('That user has no tickets already.')
                return

        # Return to user
        await ctx.send("Ticket count for **{!s}** has been updated.".format(user))


def setup(bot:CustomBot):
    x = TicketCommands(bot)
    bot.add_cog(x)
