from cogs.utils.database import DatabaseConnection as _Base


class DatabaseConnection(_Base):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def modify_user_currency(self, user, amount, currency_type):
        '''
        Modifies a user's stored money by a given amount
        '''

        db_currency = {'RS3': 'newscape', 'RS07': 'oldscape'}[currency_type]

        # Get their current money
        current_money_obj = await self.run('''
            SELECT * 
            FROM user_data
            WHERE user_id = $1
            ''', user.id
            )
        current_money = current_money_obj[0][db_currency]

        # Modify
        new_money = current_money + amount

        # Store
        sql = 'UPDATE user_data SET {}=$1 WHERE user_id=$2'.format(db_currency)
            
        await self.run(sql, new_money, user.id)


    async def set_user_currency_mode(self, user, currency_type):
        '''
        Sets a user's currency type to either oldscape or newscape
        '''

        db_currency = {'RS3': 'newscape', 'RS07': 'oldscape'}[currency_type]
        sql = 'UPDATE user_data SET currency_setting=$1 WHERE user_id=$2'
        await self.run(sql, db_currency, user.id)
