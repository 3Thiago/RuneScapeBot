from discord.ext.commands import check, Context, NotOwner


async def predicate(ctx:Context):
    default = await ctx.bot.is_owner(ctx.author)
    custom = ctx.bot.config['Owner IDs']
    if default or ctx.author.id in custom:
        return True
    raise NotOwner()


def is_owner(*args, **kwargs):
    return check(predicate)

