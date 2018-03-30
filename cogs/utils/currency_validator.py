class CurrencyType(object): pass


class OldScape(CurrencyType):
    def __str__(self):
        return 'oldscape'


class NewScape(CurrencyType):
    def __str__(self):
        return 'newscape'


def validate_currency(user_input):
    '''
    Validates a currency from a user input to either the string 'newscape' or 'oldscape'
    '''

    user_input = user_input.lower()

    if 'rs3' in user_input or 'new' in user_input:
        return NewScape()
    elif '07' in user_input or 'old' in user_input:
        return OldScape()
    else:
        return None
