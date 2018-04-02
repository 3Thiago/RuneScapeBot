from discord import Member, Guild
from cogs.utils.custom_bot import CustomBot


class JoinEvent(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    async def on_member_join(self, member:Member):
        '''
        Adds a new user to the database
        '''

        async with self.bot.database() as db:
            try:
                await db('INSERT INTO user_data (user_id) VALUES ($1)', i.id)
            except Exception: 
                pass


    async def on_guild_join(self, guild:Guild):
        '''
        Add all the users of the guild to the database
        '''

        async with self.bot.database() as db:
            for i in guild.members:
                try:
                    await db('INSERT INTO user_data (user_id) VALUES ($1)', i.id)
                except Exception: 
                    pass


def setup(bot:CustomBot):
    x = JoinEvent(bot)
    bot.add_cog(x)

