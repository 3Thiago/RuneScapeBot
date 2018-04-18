def money_fetcher(user_money):
    '''
    Modify a user input in form similar to 3.2b so that it can be returned as an integer
    '''

    user_money = user_money.lower().replace(',','')  # Remove any characters I can't int
    modifier = 0  # Modifier for decimals as well as mill, k, and bill
    modify = False  # Whether or not to modifiy for decimals
    ret = ''  # Temporary storage of what to return

    # Iterate through the input to get all the applicable characters
    for i in user_money:

        # Non-decimal character
        if i.isdigit() and modify == False:
            ret += i

        # Decimal character
        elif i.isdigit() and modify == True:
            ret += i
            modifier -= 1

        # Is a decimal, turn on modifier
        elif i == '.':
            modify = True

        # 10^n modifier
        elif i in ['m', 'k', 'b']:
            modifier += {
                'm': 6,
                'k': 3,
                'b': 9
            }[i]
            break

        # Invalid character
        else:
            return None

    # Calculate and return
    return int(ret) * (10**modifier)


def money_displayer(money_amount, accurate=False):
    '''
    Turns a given money amount into a good ol' string
    '''

    counter = 0
    money_amount = str(money_amount)
    try:
        while money_amount[-1] == '0':
            counter += 1
            money_amount = money_amount[:-1]
    except IndexError:
        pass

    if accurate == False and len(money_amount) > 3:
        extra = len(money_amount[4:])
        money_amount = money_amount[:4]
        counter += extra

    money_amount += '0' * (counter % 3)

    # See if we can make it into a.cdX instead of adc0Y
    if len(money_amount) == 4:
        while money_amount[-1] == '0': money_amount = money_amount[:-1]
        counter += 3
        money_amount = money_amount[0] + '.' + money_amount[1:]

    money_amount += {3: 'K', 6: 'M', 9: 'B', 0: ''}[(counter // 3) * 3]
    return money_amount
