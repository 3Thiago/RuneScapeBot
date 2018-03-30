def validate_currency(user_input):
    '''
    Validates a currency from a user input to either the string 'RS3' or 'RS07'
    '''

    user_input = user_input.lower()

    if 'rs3' in user_input or 'new' in user_input:
        return 'RS3'
    elif '07' in user_input or 'old' in user_input:
        return 'RS07'
    else:
        return None