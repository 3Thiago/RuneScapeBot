from cogs.utils.database import DatabaseConnection as _Base
from cogs.utils.currency_validator import OldScape, NewScape


class DatabaseConnection(_Base):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def modify_user_currency(self, user, amount, currency_type):
        '''
        Modifies a user's stored money by a given amount

        Params:
            user: Member or int
            amount: int
            currency_type: cogs.utils.currency_validator.CurrencyType
        '''

        try: user_id = user.id 
        except AttributeError: user_id = user

        # Update and store
        # eg "UPDATE user_data SET newscape=newscape+50 WHERE user_id=0;"
        sql = 'UPDATE user_data SET {0!s}={0!s}+$1 WHERE user_id=$2'.format(currency_type)            
        await self.run(sql, amount, user_id)


    async def get_user_currency(self, user, currency_type):
        '''
        Modifies a user's stored money by a given amount
        '''

        # Get their current money
        sql = 'SELECT * FROM user_data WHERE user_id = $1'
        current_money_obj = await self.run(sql, user.id)
        return current_money_obj[0][str(currency_type)]


    async def set_user_currency_mode(self, user, currency_type):
        '''
        Sets a user's currency type to either oldscape or newscape
        '''

        sql = 'UPDATE user_data SET currency_setting=$1 WHERE user_id=$2'
        await self.run(sql, str(currency_type), user.id)


    async def get_user_currency_mode(self, user):
        '''
        Gets a user's currency type
        '''

        sql = 'SELECT currency_setting FROM user_data WHERE user_id=$1'
        x = await self.run(sql, user.id)
        y = x[0]['currency_setting']
        
        if y == 'oldscape': return OldScape()
        elif y == 'newscape': return NewScape()
        return None


    async def store_die(self, die):
        '''
        Stores the information of a dice in the database
        '''

        try:
            sql = 'INSERT INTO dice VALUES ($1, $2, $3)'
            await self.run(sql, die.user_id, die.nonce, die.server_seed)
        except Exception as e:
            sql = 'UPDATE dice SET nonce=$2, server_seed=$3 WHERE user_id=$1'
            await self.run(sql, die.user_id, die.nonce, die.server_seed)

        sql = 'UPDATE user_data SET client_seed=$1 WHERE user_id=$2'
        await self.run(sql, die.client_seed, die.user_id)


    async def log_user_mod(self, **kwargs):
        '''
        Logs a user's wallet modification

        Parameters:
            message: discord.Message
                The message that triggered the modification 
            to: discord.Member
                The member whose account is being modified
            cashier: discord.Member
                A secondary user whose account is being modified due to the first user
                If this is not specified, it is assumed that the house (0) takes the burden
            amount: int
                The amount that their account is being changed by
            currency: cogs.utils.currency_validator.CurrencyType
                The type of currency that they will have their account modified by
        '''

        # Get the 'from' user (cashier)
        cashier = kwargs.get('cashier', 0)
        if cashier:
            cashier_id = cashier.id 
        else: 
            cashier_id = 0

        # Get the 'to' user
        to = kwargs.get('to')
        if type(to) == int:
            user_id = to
        else:
            user_id = to.id

        # Get the message that triggered this
        message_id = kwargs.get('message').id 

        # Get the amount 
        temp_amount = kwargs.get('amount', 0)
        currency = kwargs.get('currency')
        oldscape_change, newscape_change = (temp_amount, 0) if str(currency) == 'oldscape' else (0, temp_amount)

        # And the reason
        reason = kwargs.get('reason', None)

        # Insert the data into the database
        sql = '''
            INSERT INTO modification_log 
            (cashier_id, user_id, message_id, oldscape_mod, newscape_mod, reason) 
            VALUES 
            ($1, $2, $3, $4, $5, $6)'''
        await self.run(sql, cashier_id, user_id, message_id, oldscape_change, newscape_change, reason)

        # Insert to house modification if not deposit/withdrawal, 
        # and no specified cashier
        if reason not in ['DEPOSIT', 'WITHDRAWAL'] and cashier_id == 0:
            sql = '''
                INSERT INTO house_modification_log 
                (message_id, oldscape_mod, newscape_mod, reason) 
                VALUES ($1, $2, $3, $4)'''
            await self.run(sql, message_id, -oldscape_change, -newscape_change, reason)


    async def add_tickets_for_user(self, user, ticket_count):
        '''
        Adds new tickets to the counter for a given user
        '''

        try:
            sql = 'INSERT INTO tickets VALUES ($1, $2)'
            await self.run(sql, user.id, ticket_count)
        except Exception:
            sql = 'UPDATE tickets SET ticket_count=ticket_count+$1 WHERE user_id=$2'
            await self.run(sql, ticket_count, user.id)

