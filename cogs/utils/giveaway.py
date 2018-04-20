from random import choice
from datetime import datetime as dt, timedelta
from asyncio import sleep
from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.provably_fair import ProvablyFair
from cogs.utils.currency_validator import NewScape
from cogs.utils.money_fetcher import money_displayer


RED = 0xFF0000
GREEN = 0x00FF00


class Giveaway(object):

    def __init__(self, bot):
        self.bot = bot

        # Store the config from the JSON for easy use
        self.config = bot.config['Giveaway']
        self.channel_id = self.config['channel']
        self.timeout = self.config['timeout']
        self.duration = self.config['duration']
        self.amount = self.config['giveaway']

        # See if the giveaway is currently counting users
        self.running = False
        self.counted = set()

        # See when the giveaway was last run
        self.lastrun = dt.now()
        # self.lastrun = dt(year=2000, month=1, day=1)


    async def auto_giveaway(self):
        '''
        Runs the giveaway code for the bot
        '''

        # Get stuff ready
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)

        # Loop until the bot is closed
        while not self.bot.is_closed():
            if dt.now() >= self.lastrun + timedelta(minutes=self.timeout):

                # Make a dice for the bot
                # seed = 'GIVEAWAY ' + str(dt.now())
                # die = ProvablyFair(user_id=self.bot.user.id, client_seed=seed)

                # Tell the users about it
                with CustomEmbed() as e:
                    e.description = 'Giveaway of **{} RS3**! Type a message within the next {} seconds to be entered!'.format(money_displayer(self.amount), self.duration)
                    # e.set_footer(text='Hashed Server Seed: {}'.format(die.server_seed_hash))
                    e.colour = GREEN
                message = await channel.send(embed=e)
                self.running = True 
                self.lastrun = dt.now()

                # Wait for messages to roll in
                current_users = 0
                while dt.now() < self.lastrun + timedelta(seconds=self.duration):
                    if len(self.counted) > current_users:
                        current_users = len(self.counted)
                        try:
                            e.set_field_at(0, name='Entered Users', value=current_users)
                        except Exception:
                            e.add_new_field('Entered Users', current_users)
                        await message.edit(embed=e)
                    await sleep(1)
                self.running = False

                # Generate a random number
                # random = die.get_random()
                users = list(self.counted)

                # Check that *someone* entered
                if users:

                    # # Get a user from that
                    # randint = random['result'] * 10
                    # counter = 0
                    # while randint > 0:
                    #     try:
                    #         chosen_user = users[counter]
                    #     except IndexError:
                    #         chosen_user = users[0]
                    #         counter = 0
                    #     randint -= 1
                    chosen_user = choice(users)

                    # Wew they won
                    async with self.bot.database() as db:
                        await db.modify_user_currency(chosen_user, self.amount, NewScape())
                        await db.log_user_mod(
                            message=message, 
                            to=chosen_user, 
                            amount=self.amount, 
                            currency=NewScape(), 
                            reason='GIVEAWAY'
                            )
                    self.counted = set()

                    # Tell them about it
                    with e as e:
                        e.description = 'Giveaway over!'
                        e.colour = RED
                        # e.set_footer(text='Hashed Server Seed: {0.server_seed_hash}; Server Seed: {0.server_seed}; Client Seed: {0.client_seed}; Nonce: {0.nonce}'.format(die))
                    await message.edit(
                        content='<@{}> you just won **{} RS3**!'.format(chosen_user, money_displayer(self.amount)),
                        embed=e
                        )

                else:

                    # Nobody entered
                    await message.edit(content='Guess nobody wants any free money then :/')

            await sleep(60)
