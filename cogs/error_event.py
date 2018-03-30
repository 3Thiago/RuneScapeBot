from discord.ext.commands import Bot, CheckFailure, Context, MissingPermissions, BotMissingPermissions
from discord.ext.commands import NoPrivateMessage, NotOwner, MissingRequiredArgument, BadArgument, DisabledCommand
from discord.ext.commands import UserInputError, TooManyArguments, CommandNotFound
from cogs.utils.custom_errors import MissingRequiredRole


class ErrorEvent(object):

    def __init__(self, bot:Bot):
        self.bot = bot


    async def on_command_error(self, ctx:Context, error:CheckFailure):
        '''
        Prints the command error right back out to the user
        '''

        if isinstance(error, MissingPermissions):
            await ctx.send('You are missing the required permissions to run that command.')
        elif isinstance(error, BotMissingPermissions):
            await ctx.send('I am missing the required permissions to be able to run this command.')
        elif isinstance(error, NoPrivateMessage):
            await ctx.send('This command does not work in PMs.')
        elif isinstance(error, NotOwner):
            await ctx.send('You need to be the owner to run this command.')
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send('You are missing a required argument.')
        elif isinstance(error, BadArgument) or isinstance(error, UserInputError):
            await ctx.send('One of the arguments given for this command was invalid.')
        elif isinstance(error, DisabledCommand):
            await ctx.send('That command is disabled.')
        elif isinstance(error, TooManyArguments):
            await ctx.send('You passed too many arguments for this command.')
        elif isinstance(error, MissingRequiredRole):
            await ctx.send('You are missing a required role `{0!s}`.'.format(error))
        elif isinstance(error, CommandNotFound):
            pass  # Don't even log a command not found
        else:
            # await ctx.send('The checks for this command have failed.')
            # raise error
            print(
                'Error Event:\n'
                ' - Location {0.guild.id}/{0.channel.id}/{0.author.id}\n'
                ' - Message {0.message.clean_content}\n - Error {1}'.format(
                    ctx, error
                )
            )


def setup(bot:Bot):
    x = ErrorEvent(bot)
    bot.add_cog(x)

