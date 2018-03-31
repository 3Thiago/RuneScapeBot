from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot


class TicketCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command()
    async def tickets(self, ctx:Context):
        '''
        Shows you all of the people who have tickets, and how many
        '''

        async with self.bot.database() as db:
            data = await db('SELECT * FROM tickets ORDER BY ticket_count DESC')
        if data:
            ret = ['**{!s}** - {} tickets'.format(ctx.guild.get_member(i['user_id']), i['ticket_count']) for i in data]
        else:
            ret = ['No tickets.']
        await ctx.send('\n'.join(ret))


    @command()
    async def cleartickets(self, ctx:Context):
        '''
        Removes all of the tickets from the database
        '''

        async with self.bot.database() as db:
            data = await db('DELETE FROM tickets')
        await ctx.send('Deleted all raffle tickets from the database.')


def setup(bot:CustomBot):
    x = TicketCommands(bot)
    bot.add_cog(x)
