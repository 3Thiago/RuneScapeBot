from cogs.utils.custom_embed import CustomEmbed
from cogs.utils.cards import CARD_CLUBS, CARD_BACK


class Game(object):


    running_games = {
    }  # user, Game


    def __init__(self, dealer:int, bettor:int):
        # For editing later
        self.message = None

        # Who's playing (user IDs)
        self.dealer = dealer 
        self.bettor = bettor

        # Randomness data
        self.bettor_random = []
        self.dealer_random = []

        # Game data
        self.dealer_hand = []
        self.bettor_hand = []
        self.dealer_turn = False

        # Make it easier on myself to grab games
        self.running_games[dealer] = (self, 'dealer')
        self.running_games[bettor] = (self, 'bettor')


    @staticmethod
    def get_value_of_hand(hand) -> list:
        '''
        Calculates the values for a given hand
        '''

        val1 = 0
        val2 = 0

        if hand == CARD_CLUBS[0] * 2:
            # Both aces
            return [2, 12]

        # Each card in the hand
        for i in hand:
            try: v = CARD_CLUBS.index(i) + 1  # Index starts at 0, fix
            except ValueError: v = 0  # Back of card

            if v >= 11: v = 10  # Picture cards
            
            # Add card values
            if v == 1:
                # Ace
                val1 += 1
                val2 += 11
            else:
                # Everything else
                val1 += v 
                val2 += v 

        # Get the biggest
        m = max([val1, val2])
        if m > 21: m = min([val1, val2])
        else: return [val1, val2] if val1 != val2 else [val1]

        # Smallest is over 21
        if m > 21: return []
        return [m]


    @classmethod
    def display_value_of_hand(cls, hand) -> str:
        values = cls.get_value_of_hand(hand)
        if not values:
            return '(**Bust**)'
        return '(**' + '**, **'.join([str(i) for i in values]) + '**)'


    @classmethod
    def get_game(cls, user_id:int):
        return cls.running_games.get(user_id)


    @property
    def embed(self) -> CustomEmbed:

        nonce_data = 'Bettor rolls: {}, dealer rolls: {}'.format(
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.bettor_random]),
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.dealer_random])
            )

        card_values = [
            ', '.join(self.bettor_hand) + '\n' + self.display_value_of_hand(self.bettor_hand), 
            ', '.join(self.dealer_hand) + '\n' + self.display_value_of_hand(self.dealer_hand), 
        ]
        if self.dealer_turn == False:
            nonce_data = 'Bettor rolls: {}, dealer rolls: {}'.format(
                ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.bettor_random]),
                '({0[result]}, {0[nonce]})'.format(self.dealer_random[0])
                )
            card_values[1] = ', '.join([self.dealer_hand[0], CARD_BACK]) + '\n' + self.display_value_of_hand([self.dealer_hand[0], CARD_BACK])

        user = {True: self.dealer, False: self.bettor}[self.dealer_turn]
        role = {True: 'dealer', False: 'bettor'}[self.dealer_turn]
        colour = {True: 0x325c95, False: 0x2d5a1e}[self.dealer_turn]

        # with CustomEmbed(colour=0x325c95) as e:
        e = CustomEmbed(colour=colour)
        e.description = 'Use the `hit` or `stand` commands to continue, <@{}> ({})'.format(user, role)
        e.add_new_field('Bettor Hand', card_values[0])
        e.add_new_field('House Hand', card_values[1])
        e.set_footer(text=nonce_data)
        return e


    @classmethod
    def is_hand_bust(cls, hand) -> bool:
        return cls.get_value_of_hand(hand) == []


    @classmethod
    def is_hand_21(cls, hand) -> bool:
        return max(cls.get_value_of_hand(hand)) == 21

    @property
    def winner(self):
        '''
        Returns the ID of the user who won the game
        '''

        if self.is_hand_bust(self.bettor_hand):
            # bettor is bust
            return (self.dealer, 'dealer')
        else:
            if self.is_hand_bust(self.dealer_hand):
                # Dealer is bust
                return (self.bettor, 'bettor')

        # return who has the highest value
        if self.get_value_of_hand(self.dealer_hand) >= self.get_value_of_hand(self.bettor_hand):
            return (self.dealer , 'dealer')
        return (self.bettor, 'bettor')
