from enum import Enum, unique

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


@unique
class Operator(str, Enum):
    and_ = ' AND '
    or_ = ' OR '
    eq = ' = '
    ne = ' != '
    lt = ' < '
    le = ' <= '
    gt = ' > '
    ge = ' >= '
    add = ' + '
    sub = ' - '
    mul = ' * '
    div = ' / '
    mod = ' % '
    pow = ' ^ '
    contains = ' @> '
    contained_by = ' <@ '
    like = ' LIKE '
    cat = ' || '
    in_ = ' in '
    from_ = ' from '
    for_ = ' for '
    factorial = '!'
    cast = '::'
    asc = ' ASC'
    desc = ' DESC'
    comma = ', '
    on = ' ON '


@unique
class LeftOperator(str, Enum):
    neg = '-'
    sqrt = '|/ '
    abs = '@ '


PRECEDENCE = {
    Operator.cast: 130,

    LeftOperator.neg: 120,
    LeftOperator.sqrt: 120,
    LeftOperator.abs: 120,

    Operator.pow: 100,
    Operator.mod: 90,
    Operator.mul: 80,
    Operator.div: 70,
    Operator.add: 60,
    Operator.sub: 50,

    Operator.contains: 35,
    Operator.contained_by: 35,
    Operator.like: 35,
    Operator.cat: 35,
    Operator.in_: 35,
    Operator.from_: 35,

    Operator.eq: 40,
    Operator.ne: 40,
    Operator.lt: 40,
    Operator.le: 40,
    Operator.gt: 40,
    Operator.ge: 40,

    Operator.asc: 30,
    Operator.desc: 30,

    Operator.and_: 20,
    Operator.or_: 10,
    Operator.comma: 0,
    Operator.on: -10,
}


class SqlBlock(Component):
    __slots__ = 'v1', 'op', 'v2'

    def __init__(self, v1, *, op=None, v2=None):
        self.v1 = v1
        self.op = op
        self.v2 = v2

    def operate(self, op: Operator, v2=None):
        if self.op:
            # op already completed
            return SqlBlock(self, op=op, v2=v2)
        else:
            self.op = op
            self.v2 = v2
            return self

    def __and__(self, other):
        return self.operate(Operator.and_, other)

    def __or__(self, other):
        return self.operate(Operator.or_, other)

    def __eq__(self, other):
        return self.operate(Operator.eq, other)

    def __ne__(self, other):
        return self.operate(Operator.ne, other)

    def __lt__(self, other):
        return self.operate(Operator.lt, other)

    def __le__(self, other):
        return self.operate(Operator.le, other)

    def __gt__(self, other):
        return self.operate(Operator.gt, other)

    def __ge__(self, other):
        return self.operate(Operator.ge, other)

    def __add__(self, other):
        return self.operate(Operator.add, other)

    def __sub__(self, other):
        return self.operate(Operator.sub, other)

    def __mul__(self, other):
        return self.operate(Operator.mul, other)

    def __truediv__(self, other):
        return self.operate(Operator.div, other)

    def __mod__(self, other):
        return self.operate(Operator.mod, other)

    def __pow__(self, other):
        return self.operate(Operator.pow, other)

    def __invert__(self):
        return Not(self)

    def __neg__(self):
        return LeftOp(LeftOperator.neg, self)

    def sqrt(self):
        return LeftOp(LeftOperator.sqrt, self)

    def abs(self):
        return LeftOp(LeftOperator.abs, self)

    def factorial(self):
        return self.operate(Operator.factorial)

    def contains(self, other):
        return self.operate(Operator.contains, other)

    def contained_by(self, other):
        return self.operate(Operator.contained_by, other)

    def like(self, other):
        return self.operate(Operator.like, other)

    def cat(self, other):
        return self.operate(Operator.cat, other)

    def in_(self, other):
        return self.operate(Operator.in_, other)

    def from_(self, other):
        return self.operate(Operator.from_, other)

    def for_(self, other):
        return self.operate(Operator.for_, other)

    def cast(self, cast_type):
        return self.operate(Operator.cast, V(cast_type))

    def asc(self):
        return self.operate(Operator.asc)

    def desc(self):
        return self.operate(Operator.desc)

    def comma(self, other):
        return self.operate(Operator.comma, other)

    def on(self, other):
        return self.operate(Operator.on, other)

    def _should_bracket(self, v):
        if self.op:
            sub_op = getattr(v, 'op', None)
            if sub_op and PRECEDENCE.get(self.op, 0) > PRECEDENCE.get(sub_op, -1):
                return True

    def _bracket(self, v):
        if self._should_bracket(v):
            yield Literal('(')
            yield v
            yield Literal(')')
        else:
            yield v

    def render(self):
        yield from self._bracket(self.v1)
        if self.op:
            yield Literal(self.op.value)
            if self.v2:
                yield from self._bracket(self.v2)


def as_sql_block(n):
    if isinstance(n, SqlBlock):
        return n
    else:
        return SqlBlock(n)


class Func(SqlBlock):
    allow_unsafe = False

    def __init__(self, func, *args):
        if not self.allow_unsafe:
            check_word(func)
        super().__init__(args, op=func)

    def operate(self, op: Operator, v2=None):
        return SqlBlock(self, op=op, v2=v2)

    def render(self):
        yield Literal(self.op + '(')
        yield from yield_sep(self.v1)
        yield Literal(')')


class LeftOp(Func):
    allow_unsafe = True

    def render(self):
        yield Literal(self.op.value)
        yield from self._bracket(self.v1[0])


class Not(Func):
    def __init__(self, v):
        super().__init__('NOT', v)

    def __invert__(self):
        return self.v1[0]


class Var(SqlBlock):
    def __init__(self, v1, *, op: Operator=None, v2=None):
        super().__init__(VarLiteral(v1), op=op, v2=v2)


S = SqlBlock
V = Var
