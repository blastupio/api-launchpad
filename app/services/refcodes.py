from random import choice


def generate_code():
    allowed_symbols = list("abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPRQRSTUVWXYZ23456789")
    return "".join([choice(allowed_symbols) for _ in range(4)])
