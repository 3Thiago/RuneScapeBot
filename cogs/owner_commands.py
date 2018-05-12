from traceback import format_exc
from aiohttp import ClientSession
from asyncio import iscoroutine
from discord import Game, Embed
from discord.ext.commands import command, group, Context, NotOwner, MissingRequiredArgument
from asyncpg.exceptions import __all__ as PostgresError
from cogs.utils.custom_bot import CustomBot
from cogs.utils.owner_check import predicate as is_owner


class OwnerCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)


    def __unload(self):
        self.session.close()


    async def __local_check(self, ctx:Context):
        x = await is_owner(ctx)
        if x:
            return True
        raise NotOwner()


    @command()
    async def runsql(self, ctx:Context, *, content:str):
        '''
        Runs a line of SQL into the sparcli database
        '''

        async with self.bot.database() as db:
            x = await db(content) or 'No content.'
        if type(x) in [str, type(None)]:
            await ctx.send(x)
            return

        # Get the results into groups
        column_headers = list(x[0].keys())
        grouped_outputs = {}
        for i in column_headers:
            grouped_outputs[i] = []
        for guild_data in x:
            for i, o in guild_data.items():
                grouped_outputs[i].append(str(o))

        # Everything is now grouped super nicely
        # Now to get the maximum length of each column and add it as the last item
        for key, item_list in grouped_outputs.items():
            max_len = max([len(i) for i in item_list + [key]])
            grouped_outputs[key].append(max_len)

        # Format the outputs and add to a list
        key_headers = []
        temp_output = []
        for key, value in grouped_outputs.items():
            # value is a list of unformatted strings
            key_headers.append(format(key, '<' + str(value[-1])))
            formatted_values = [format(i, '<' + str(value[-1])) for i in value[:-1]]
            # string_value = '|'.join(formatted_values)
            temp_output.append(formatted_values)
        key_string = '|'.join(key_headers)

        # Rotate the list because apparently I need to
        output = []
        for i in range(len(temp_output[0])):
            temp = []
            for o in temp_output:
                temp.append(o[i])
            output.append('|'.join(temp))

        # Add some final values before returning to the user
        line = '-' * len(key_string)
        output = [key_string, line] + output 
        string_output = '\n'.join(output)
        await ctx.send('```\n{}```'.format(string_output))


    @group()
    async def profile(self, ctx:Context):
        '''
        A parent group for the different profile commands
        '''

        pass


    @profile.command(aliases=['username'])
    async def name(self, ctx:Context, *, username:str):
        '''
        Lets you change the username of the bot
        '''

        if len(username) > 32:
            await ctx.send('That username is too long to be compatible with Discord.')
            return 

        await self.bot.user.edit(username=username)
        await ctx.send('Done.')


    @profile.command(aliases=['picture'])
    async def avatar(self, ctx:Context, *, url:str=None):
        '''
        Allows you to change the avatar of the bot to a URL or attached picture
        '''

        # Make sure a URL is passed
        if url == None:
            try:
                url = ctx.message.attachments[0].url
            except IndexError:
                raise MissingRequiredArgument(self.avatar.params['url'])

        # Get the image
        async with self.session.get(url) as r:
            content = await r.read()

        # Edit the profile
        await self.bot.user.edit(avatar=content)
        await ctx.send('Done.')


    @profile.command()
    async def game(self, ctx:Context, game_type:int=None, *, name:str=None):
        '''
        Change the game that the bot is playing
        '''

        if not name: 
            name = self.bot.config['Game']['name']
        if not game_type:
            game_type = self.bot.config['Game']['type']
        game = Game(name=name, type=game_type)
        await self.bot.change_presence(activity=game)
        await ctx.send('Done.')


    @command()
    async def embed(self, ctx:Context, *, content:str):
        '''
        Creates an embed from raw JSON data
        '''

        e = Embed.from_data(eval(content))
        await ctx.send(embed=e)


    @command()
    async def kill(self, ctx:Context):
        '''
        Turns off the bot and anything related to it
        '''

        async with self.bot.database() as db:
            for i in self.bot._die.values():
                await db.store_die(i)
        await ctx.send('Turning off now.')
        await self.bot.logout()


    @command()
    async def ev(self, ctx:Context, *, content:str):
        '''
        Runs some text through Python's eval function
        '''

        try:
            ans = eval(content)
        except Exception as e:
            await ctx.send('```py\n' + format_exc() + '```')
            return
        if iscoroutine(ans):
            ans = await ans
        await ctx.send('```py\n' + str(ans) + '```')


    @command(aliases=['uld'])
    async def unload(self, ctx:Context, *cog_name:str):
        '''
        Unloads a cog from the bot
        '''

        self.bot.unload_extension('cogs.' + '_'.join([i.lower() for i in cog_name]))
        await ctx.send('Cog unloaded.')


    @command()
    async def load(self, ctx:Context, *cog_name:str):
        '''
        Unloads a cog from the bot
        '''

        self.bot.load_extension('cogs.' + '_'.join([i.lower() for i in cog_name]))
        await ctx.send('Cog loaded.')


    @command(aliases=['rld'])
    async def reload(self, ctx:Context, *, cog_name:str):
        '''
        Unloads a cog from the bot
        '''

        self.bot.unload_extension('cogs.' + cog_name.lower())
        try:
            self.bot.load_extension('cogs.' + cog_name.lower())
        except Exception as e:
            await ctx.send('```py\n' + format_exc() + '```')
            return
        await ctx.send('Cog reloaded.')


    @command()
    async def leaveguild(self, ctx:Context, guild_id:int):
        '''
        Leaves a given guild
        '''

        guild = self.bot.get_guild(guild_id)
        await guild.leave()
        await ctx.send('Done.')


def setup(bot:CustomBot):
    x = OwnerCommands(bot)
    bot.add_cog(x)
