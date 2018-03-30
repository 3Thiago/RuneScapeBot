import asyncpg


class DatabaseConnection(object):

    config = None


    def __init__(self):
        self.db = None


    async def __aenter__(self):
        self.db = await self.get_database_connection()
        return self


    async def __aexit__(self, exc_type, exc, tb):
        await self.db.close()


    async def get_database_connection(self):
        '''
        Creates the database connection to postgres using the data from the config files
        '''

        conn = await asyncpg.connect(**DatabaseConnection.config)
        return conn


    async def __call__(self, sql:str, *args):
        '''
        Runs a line of SQL using the internal database
        '''

        # Runs the SQL
        x = await self.db.fetch(sql, *args)

        # If it got something, return the dict, else None
        if x:
            return x
        return None
