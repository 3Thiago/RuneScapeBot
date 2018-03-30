from cogs.utils.database import DatabaseConnection as _Base
from cogs.utils.currency_validator import OldScape, NewScape


class DatabaseConnection(_Base):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def modify_user_currency(self, user, amount, currency_type):
        '''
        Modifies a user's stored money by a given amount

        Params:
            user: Member
            amount: int
            currency_type: cogs.utils.currency_validator.CurrencyType
        '''

        # Get their current money
        current_money_obj = await self.run('''
            SELECT * 
            FROM user_data
            WHERE user_id = $1
            ''', user.id
            )
        current_money = current_money_obj[0][str(currency_type)]

        # Modify
        new_money = current_money + amount

        # Store
        sql = 'UPDATE user_data SET {!s}=$1 WHERE user_id=$2'.format(currency_type)
            
        await self.run(sql, new_money, user.id)


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
        await self.run(sql, str(db_currency), user.id)


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

