from enum import Enum
from .components import Component, Literal, VarLiteral, check_word, yield_sep

__all__ = (
    'LogicError',
    'SqlBlock',
    'Func',
    'Not',
    'Var',
    'S',
    'V',
)


class LogicError(RuntimeError):
    pass


class Operator(str, Enum):
    and_ = 'AND'
    or_ = 'OR'
    eq = '='
    ne = '!='
    lt = '<'
    le = '<='
    gt = '>'
    ge = '>='
    add = '+'
    sub = '-'
    mul = '*'
    div = '/'
    mod = '%'
    pow = '^'
    contains = '@>'
    contained_by = '<@'
    like = 'LIKE'
    cat = '||'
    sqrt = '|/'       # single arg TODO move to functions
    abs = '@'         # single arg
    factorial = '!!'  # single arg, use prefix operator for simplicity


class SqlBlock(Component):
    __slots__ = 'v1', 'op', 'v2'

    def __init__(self, v1, *, op: Operator=None, v2=None):
        self.v1 = v1
        self.op = op
        self.v2 = v2

    def fill(self, op: Operator, v2=None):
        if self.op:
            # op already completed
            return SqlBlock(self, op=op, v2=v2)
        else:
            self.op = op
            self.v2 = v2
            return self

    def __and__(self, other):
        return self.fill(Operator.and_, other)

    def __or__(self, other):
        return self.fill(Operator.or_, other)

    def __eq__(self, other):
        return self.fill(Operator.eq, other)

    def __ne__(self, other):
        return self.fill(Operator.ne, other)

    def __lt__(self, other):
        return self.fill(Operator.lt, other)

    def __le__(self, other):
        return self.fill(Operator.le, other)

    def __gt__(self, other):
        return self.fill(Operator.gt, other)

    def __ge__(self, other):
        return self.fill(Operator.ge, other)

    def __add__(self, other):
        return self.fill(Operator.add, other)

    def __sub__(self, other):
        return self.fill(Operator.sub, other)

    def __mul__(self, other):
        return self.fill(Operator.mul, other)

    def __truediv__(self, other):
        return self.fill(Operator.div, other)

    def __mod__(self, other):
        return self.fill(Operator.mod, other)

    def __pow__(self, other):
        return self.fill(Operator.pow, other)

    def contains(self, other):
        return self.fill(Operator.contains, other)

    def contained_by(self, other):
        return self.fill(Operator.contained_by, other)

    def like(self, other):
        return self.fill(Operator.like, other)

    def cat(self, other):
        return self.fill(Operator.cat, other)

    def __invert__(self):
        return Not(self)

    def render(self):
        if isinstance(self.v1, Component) and getattr(self.v1, 'op', None) != self.op:
            yield Literal('(')
            yield self.v1
            yield Literal(')')
        else:
            yield self.v1
        if self.op:
            yield Literal(' ' + self.op.value + ' ')
            if self.v2:
                yield self.v2


class Func(SqlBlock):
    __slots__ = 'func', 'args'

    def __init__(self, func, *args):
        check_word(func)
        self.func = func
        self.args = args

    def fill(self, op: Operator, v2=None):
        return SqlBlock(self, op=op, v2=v2)

    def render(self):
        yield Literal(self.func + '(')
        yield from yield_sep(self.args)
        yield Literal(')')


class Not(Func):
    def __init__(self, v):
        super().__init__('NOT', v)

    def __invert__(self):
        return self.args[0]


class Var(SqlBlock):
    def __init__(self, v1, *, op: Operator=None, v2=None):
        super().__init__(VarLiteral(v1), op=op, v2=v2)


S = SqlBlock
V = Var
