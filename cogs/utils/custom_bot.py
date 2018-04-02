from datetime import datetime as dt
from json import load
from discord import Message
from discord.ext import commands
from cogs.utils.runescape_database import DatabaseConnection
from cogs.utils.provably_fair import ProvablyFair
from cogs.utils.giveaway import Giveaway


class CustomBot(commands.AutoShardedBot):


    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.get_prefix, **kwargs)
        self.config = {}  # Used to store the bot config file
        self.default_prefix = kwargs['default_prefix']  # Used as a fallback for the prefix
        self.startup = dt.now()  # Used to check uptime
        with open('./config/bot.json') as a:
            data = load(a)
        self.config = data
        self.database = DatabaseConnection
        DatabaseConnection.config = data['Database']
        self._die = {}

        self.giveaway = Giveaway(self)
        self.giveaway_task = self.loop.create_task(self.giveaway.auto_giveaway())


    def get_die(self, user_id):
        return self._die.get(user_id)


    def set_die(self, user_id, die):
        self._die[user_id] = die


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
        return dt.now() - self.startup


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

            print('Getting user die... ', end='')
            data = await db('SELECT * FROM dice, user_data WHERE dice.user_id=user_data.user_id')
            if data:
                for i in data:
                    self.set_die(i['user_id'], ProvablyFair.from_database(i))
            print('done')

