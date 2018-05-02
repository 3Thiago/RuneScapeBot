def random_from_list(roll:float, items:list):
    '''
    Gets a random item from a given unshuffled list where each item has
    an equal probability of being picked and the roll is a percentage of the
    way through the list (a float between 0 and 100 inclusive)
    '''

    calc = [i for i in range(1, len(items)+1) if roll >= (100*i)/len(items)]
    rolled_item = items[len(calc)] 
    return rolled_item
