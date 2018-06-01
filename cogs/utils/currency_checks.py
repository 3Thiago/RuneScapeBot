from discord.ext.commands import Context, check
from cogs.utils.custom_errors import NoDiceGenerated, NoCurrencySet


def has_dice(*args, **kwargs):
    async def predicate(ctx:Context):
        d = await ctx.bot.aget_die(ctx.author.id)
        if d:
            if d.valid:
                return True
        raise NoDiceGenerated()
    return check(predicate)


def has_set_currency(*args, **kwargs):
    async def predicate(ctx:Context):
        async with ctx.bot.database() as db:
            x = await db.get_user_currency_mode(ctx.author)
        if x:
            return True
        raise NoCurrencySet()
    return check(predicate)


