from secrets import token_hex
from hashlib import sha256, sha512
from hmac import new


class ProvablyFair(object):

    def __init__(self, user_id=None, client_seed=None, *, server_seed=None, nonce=-1):
        self.valid = True
        self.user_id = user_id
        self.nonce = nonce
        self.client_seed = client_seed if client_seed else token_hex(10)
        if not server_seed:
            self.server_seed, self.server_seed_hash = self.get_server_seed()
        else:
            self.server_seed, self.server_seed_hash = self._hash_server_seed(server_seed)


    @classmethod
    def from_database(cls, data):
        return cls(
            client_seed=data['client_seed'], 
            server_seed=data['server_seed'], 
            nonce=data['nonce'],
            user_id=data['user_id']
            )


    def set_client_seed(self, client_seed):
        self.client_seed = client_seed


    @staticmethod
    def get_server_seed():
        '''
        Generates a new server seed to use for future rolls
        '''

        server_seed = token_hex(20)
        server_seed_hash_object = sha256(server_seed.encode())
        server_seed_hash = server_seed_hash_object.hexdigest()
        return server_seed, server_seed_hash


    @staticmethod
    def _hash_server_seed(server_seed):
        '''
        Hashes and stores a given server seed - DEBUGGING ONLY
        '''

        server_seed_hash_object = sha256(server_seed.encode())
        server_seed_hash = server_seed_hash_object.hexdigest()
        return server_seed, server_seed_hash


    def invalidate(self):
        '''
        Ends the game
        '''

        return {
            'server_seed': self.unhash_server_seed()
        }


    def unhash_server_seed(self):
        '''
        Gets the unhashed server seed from the server
        This will invalidate all future rolls using that server seed [hash]
        '''

        self.valid = False
        return self.server_seed


    def get_random(self, *, nonce=None):
        '''
        Generates a provably random number given a client seed and a 
        pre-generated server seed hash
        '''

        # Make sure it's still valid
        if not self.valid:
            raise Exception('This server seed is no longer valid.')

        # Get a nonce to use
        if not nonce: 
            self.nonce += 1
            nonce = self.nonce

        # HMAC it up
        msg_str = '{}-{}'.format(self.client_seed, nonce)
        key = self.server_seed.encode()
        msg = msg_str.encode()
        dig = new(key, msg=msg, digestmod=sha512)

        # Get the number
        full_number = dig.hexdigest()
        counter = 0
        while True:
            number_str = full_number[counter:counter+5]
            number = int(number_str, 16)
            if number > 999999:
                counter += 5
            else:
                break

        # Return results
        return {
            'result': (number % (10**4)) / 100,
            'nonce': nonce,
            'server_seed_hash': self.server_seed_hash,
            'client_seed': self.client_seed
        }
