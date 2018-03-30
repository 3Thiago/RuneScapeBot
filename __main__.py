from glob import glob
from discord import Game
from cogs.utils.custom_bot import CustomBot


bot = CustomBot(
    default_prefix='!',
    pm_help=True
)


# List all files in the Cogs directory that end in .py
extensions = []
for filepath in glob('./cogs/[!_]*.py'):
    file = filepath.replace('\\', '/').split('/')[-1]  # Linux + Windows compatible
    filename = 'cogs.' + file[:-3]  # Remove .py
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
            exc = '{}: {}'.format(type(e).__name__, e)
            print(' - Failed to load extension {}\n       {}'.format(ext, exc))

    print("All extensions loaded")

    print('Updating presence... ', end='')
    game = Game(**bot.config['Game'])
    await bot.change_presence(game=game)
    print('updated')
    print('\nAll ready.\n')


bot.run_custom()
