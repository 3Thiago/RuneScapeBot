from datetime import datetime
from json import load
from discord import Message
from discord.ext import commands
from cogs.utils.runescape_database import DatabaseConnection


class CustomBot(commands.AutoShardedBot):


    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.get_prefix, **kwargs)
        self.config = {}  # Used to store the bot config file
        self.default_prefix = kwargs['default_prefix']  # Used as a fallback for the prefix
        self.startup = datetime.now()  # Used to check uptime
        with open('./config/bot.json') as a:
            data = load(a)
        self.config = data
        self.database = DatabaseConnection
        DatabaseConnection.config = data['Database']


    def regen_config(self):
        '''
        Rereads the bot config file to memory
        '''

        with open('./config/bot.json') as a:
            data = load(a)
        self.config = data
        self._log_channel = None


    def run_custom(self):
        token = self.config["Bot Token"]
        self.run(token)


    def get_uptime(self):
        return datetime.now() - self.startup


    async def get_prefix(self, message:Message):
        '''
        Lets you get a prefix for the guild that you're in
        '''

        mentions = '<@{0.user.id}> ,<@!{0.user.id}> '.format(self).split(',')
        return [self.default_prefix] + mentions


    async def run_database_setup(self):
        '''
        This runs a database setup for the bot
        '''

        print('Checking database...')

        user_list = []
        for i in self.guilds:
            for o in i.members:
                user_list.append(o)

        async with DatabaseConnection() as db:
            # Go through each guild
            for i in user_list:
                print(' - Checking for user {0.id}... '.format(i), end='')

                # Get the current info from the user settings
                current_info = await db('SELECT * FROM user_data WHERE user_id=$1', i.id)

                # If there's none, create some
                if current_info == None:
                    print('not found - inserting... ', end='')
                    await db('INSERT INTO user_data (user_id) VALUES ($1)', i.id)
                    print('done')

                # If there is, do nothing
                else:
                    print('present')
