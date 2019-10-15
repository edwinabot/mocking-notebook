from randomizers import get_random_ratio, get_random_natural


def do_example_three():
    number = get_random_ratio()
    print(f'\nI got {number}')
    return number


def do_example_three_again():
    number = get_random_natural() * get_random_ratio()
    print(f'\nI got {number}')
    return number
