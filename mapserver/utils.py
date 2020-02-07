import string
import random


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def rs8():
    return random_string(8)


def rs10():
    return random_string(10)


def rs12():
    return random_string(12)

