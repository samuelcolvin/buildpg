from .logic import Func, SqlBlock


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


def _get_block(n):
    if isinstance(n, SqlBlock):
        return n
    else:
        return SqlBlock(n)


def sqrt(n):
    return _get_block(n).sqrt()


def abs(n):
    return _get_block(n).abs()


def factorial(n):
    return _get_block(n).factorial()
