from discord.ext.commands import Context
from cogs.utils.custom_bot import CustomBot


class CommandEvent(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    async def on_command(self, ctx:Context):
        '''
        Count the amount of times that any given command has been called
        '''

        command = ctx.command.name
        if ctx.invoked_subcommand:
            command = ctx.command.name + ' ' + ctx.invoked_subcommand.name
        author_id = ctx.author.id
        guild_id = 0 if not ctx.guild else ctx.guild.id

        async with self.bot.database() as db:
            sql = 'INSERT INTO command_log (user_id, message_id, guild_id, command_name, message_text, time) VALUES ($1, $2, $3, $4, $5, $6)'
            await db(sql, author_id, ctx.message.id, guild_id, command, ctx.message.content, ctx.message.created_at)

            try:
                await db(
                    'INSERT INTO commands_run (user_id, command_name, count, guild_id) VALUES ($1, $2, $3, $4)', 
                    author_id, 
                    command, 
                    1,
                    guild_id
                )
            except Exception as e:
                count_obj = await db(
                    'SELECT count FROM commands_run WHERE user_id=$1 AND command_name=$2 AND guild_id=$3',
                    author_id,
                    command,
                    guild_id
                )
                count = count_obj[0]['count']
                count += 1
                await db(
                    'UPDATE commands_run SET count=$1 WHERE user_id=$2 AND command_name=$3 AND guild_id=$4',
                    count,
                    author_id,
                    command,
                    guild_id
                )


def setup(bot:CustomBot):
    x = CommandEvent(bot)
    bot.add_cog(x)
