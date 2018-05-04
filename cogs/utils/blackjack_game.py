from cogs.utils.cards import CARD_CLUBS, CARD_BACK


class Game(object):

    running_games = {
    }  # user, Game

    def __init__(self, dealer:int, bettor:int):
        # For editing later
        self.message = None

        # Who's playing
        self.dealer = dealer 
        self.bettor = bettor

        # Randomness data
        self.bettor_random = None
        self.dealer_random = None

        # Game data
        self.dealer_hand = []
        self.bettor_hand = []
        self.dealer_turn = False

        # Random data

        # Make it easier on myself to grab games
        self.running_games[dealer] = (self, 'dealer')
        self.running_games[bettor] = (self, 'bettor')

        self.d = None

    def get_value(self, hand):
        val1 = 0
        val2 = 0
        for i in hand:
            try:
                v = CARD_CLUBS.index(i) + 1  # Index starts at 0, so card_ten will reflect 10 and not 9
            except IndexError:
                v = 0

            # Picture cards
            if v >= 11:
                v = 10

            # Ace
            if v == 1:
                val1 += 1
                val2 += 11
            else:
                val1 += v 
                val2 += v 

        # Get the biggest
        m = max([val1, val2])
        if m > 21:
            # It's over 21, get smallest
            m = min([val1, val2])
        # Biggest is valid
        else:
            return '(**' + str(m) + '**)'

        # Smallest is over 21
        if m > 21:
            return '(**Bust**)' 
        return '(**' + str(m) + '**)'

    @classmethod
    def get_game(cls, user_id:int):
        return cls.running_games.get(user_id)

    @property
    def embed(self):

        nonce_data = 'Bettor rolls: {}, dealer rolls: {}'.format(
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.bettor_random]),
            ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.dealer_random])
            )

        display = [
            ', '.join(self.bettor_hand) + '\n' + self.get_value(self.bettor_hand), 
            ', '.join(self.dealer_hand) + '\n' + self.get_value(self.dealer_hand)
        ]
        if self.dealer_turn == False:
            nonce_data = 'Bettor rolls: {}, dealer rolls: {}'.format(
                ', '.join(['({0[result]}, {0[nonce]})'.format(i) for i in self.bettor_random]),
                '({0[result]}, {0[nonce]})'.format(self.dealer_random[0])
                )
            display[1] = ', '.join([self.dealer_hand[0], CARD_BACK]) + '\n' + self.get_value(self.dealer_hand[:1])

        user = {True: self.dealer, False: self.bettor}[self.dealer_turn]
        role = {True: 'dealer', False: 'bettor'}[self.dealer_turn]

        # with CustomEmbed(colour=0x325c95) as e:
        e = CustomEmbed(colour=0x325c95)
        e.description = 'Use the `hit` or `stand` commands to continue, <@{}> ({})'.format(user, role)
        e.add_new_field('Bettor Hand', display[0])
        e.add_new_field('House Hand', display[1])
        e.set_footer(text=nonce_data)
        return e

    @property
    def is_bust(self):
        if self.dealer_turn:
            return self.get_value(self.dealer_hand) == '(**Bust**)'
        return self.get_value(self.bettor_hand) == '(**Bust**)'

    @property
    def is_21(self):
        if self.dealer_turn:
            return self.get_value(self.dealer_hand) == '(**21**)'
        return self.get_value(self.bettor_hand) == '(**21**)'
