# pylint:disable=invalid-name
"""
Test GPIO module
"""
import random

BOARD = 1
OUT = 1
IN = 1


def setmode(mode):
    print('setmode:', mode)


def setup(*args, **kwargs):
    print('setup:', args, kwargs)


def output(a, b):
    print('output:', a, b)


def cleanup():
    print('cleanup')


def setwarnings(flag):
    print('setwarnings:', flag)


def input(pin):
    value = random.randint(0, 1) == 1
    print('input', pin, value)
    return value
