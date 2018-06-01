from glob import glob
from discord import Game
from cogs.utils.custom_bot import CustomBot


bot = CustomBot(
    default_prefix='.',
    pm_help=True,
    run_giveaway=True
)


# List all files in the Cogs directory that end in .py
extensions = []
cog_files = glob('./cogs/[!_]*.py') + glob('./cogs/games/[!_]*.py')
for filepath in cog_files:
    file = filepath.replace('\\', '/').replace('/', '.')  # Linux + Windows compatible
    filename = file[2:-3]  # Remove .py and ./
    extensions.append(filename)


@bot.event
async def on_ready():
    print('Booted and ready for action')
    print(' - {0.user}'.format(bot))
    print(' - {0.user.id}'.format(bot))

    await bot.run_database_setup()

    print('Loading extensions...')
    for ext in extensions:
        try:
            bot.load_extension(ext)
            print(' - Loaded extension', ext)
        except Exception as e:
            # raise e
            exc = '{}: {}'.format(type(e).__name__, e)
            print(' - Failed to load extension {}\n       {}'.format(ext, exc))

    print("All extensions loaded")

    print('Updating presence... ', end='')
    game = Game(**bot.config['Game'])
    await bot.change_presence(activity=game)
    print('updated')
    print('\nAll ready.\n')


bot.run_custom()
