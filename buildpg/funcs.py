from . import logic


def AND(arg, *args):
    v = logic.as_sql_block(arg)
    for a in args:
        v &= a
    return v


def OR(arg, *args):
    v = logic.as_sql_block(arg)
    for a in args:
        v |= a
    return v


def comma_sep(arg, *args):
    v = logic.as_sql_block(arg)
    for a in args:
        v = v.comma(a)
    return v


def cast(v, cast_type):
    return logic.as_sql_block(v).cast(cast_type)


def upper(string):
    return logic.Func('upper', string)


def lower(string):
    return logic.Func('lower', string)


def length(string):
    return logic.Func('length', string)


def left(string, n):
    return logic.Func('left', string, n)


def right(string, n):
    return logic.Func('right', string, n)


def sqrt(n):
    return logic.as_sql_block(n).sqrt()


def abs(n):
    return logic.as_sql_block(n).abs()


def factorial(n):
    return logic.as_sql_block(n).factorial()


def position(substring, string):
    return logic.Func('position', logic.SqlBlock(substring).in_(string))


def substring(string, pattern, for_=None):
    a = logic.SqlBlock(string,).from_(pattern)
    if for_:
        a = a.for_(for_)
    return logic.Func('substring', a)
