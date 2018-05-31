from .logic import Func, SqlBlock


def _as_block(n):
    if isinstance(n, SqlBlock):
        return n
    else:
        return SqlBlock(n)


def AND(arg, *args):
    v = _as_block(arg)
    for a in args:
        v &= a
    return v


def OR(arg, *args):
    v = _as_block(arg)
    for a in args:
        v |= a
    return v


def cast(v, cast_type):
    return _as_block(v).cast(cast_type)


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


def sqrt(n):
    return _as_block(n).sqrt()


def abs(n):
    return _as_block(n).abs()


def factorial(n):
    return _as_block(n).factorial()
