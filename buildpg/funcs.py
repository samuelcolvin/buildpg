from .logic import Func


def upper(string):
    return Func('upper', string)


def lower(string):
    return Func('lower', string)


def length(string):
    return Func('length', string)


def left(string, n):
    return Func('left', string, n)


def right(string, n):
    return Func('right', string, n)
