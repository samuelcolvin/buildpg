from enum import Enum
from .components import Component

# class Operator(IntEnum):
#     eq = 1
#     ne = 2
#     lt = 3
#     le = 4
#     gt = 5
#     ge = 6
#     add = 7
#     sub = 8
#     mul = 9
#     div = 10
#     mod = 11
#     pow = 12
#     in_ = 13
#     like = 14
#     sqrt = 15       # single arg
#     abs = 16        # single arg
#     factorial = 17  # single arg
#
#
# OP_LOOKUP = {
#     Operator.eq: '=',
#     Operator.ne: '!=',
#     Operator.lt: '<',
#     Operator.le: '<=',
#     Operator.gt: '>',
#     Operator.ge: '>=',
#     Operator.add: '+',
#     Operator.sub: '-',
#     Operator.mul: '*',
#     Operator.div: '/',
#     Operator.mod: '%',
#     Operator.pow: '^',
#     Operator.in_: 'IN',
#     Operator.like: 'LIKE',
#     Operator.sqrt: '|/',
#     Operator.abs: '@',
#     Operator.factorial: '!!',  # use prefix operator for simplicity
# }


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
    in_ = 'IN'
    like = 'LIKE'
    sqrt = '|/'       # single arg TODO move to functions
    abs = '@'         # single arg
    factorial = '!!'  # single arg, use prefix operator for simplicity


class Operation(Component):
    def __init__(self, v1, op: Operator=None, v2=None):
        self.v1 = v1
        self.op = op
        self.v2 = v2

    def fill(self, op: Operator, v2):
        if self.op:
            raise LogicError(f'operation already filled ({self.v1}')
        self.op = op
        self.v2 = v2
        return self

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

    def __eq__(self, other):
        return self.fill(Operator.eq, other)

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(self, other)

    def __invert__(self):
        return And(self, inverted=True)

    def __repr__(self):
        return f'<Op"{self.v1}" {self.op.value} "{self.v2}">'


class _AndOr(Component):
    op = NotImplemented

    def __init__(self, *phrases, inverted: bool=False):
        self.phrases = phrases
        self.inverted = inverted

    def __invert__(self):
        self.inverted = not self.inverted
        return self


class And(_AndOr):
    op = Operator.and_

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        self.phrases += other


class Or(_AndOr):
    op = Operator.or_

    def __or__(self, other):
        self.phrases += other

    def __and__(self, other):
        return And(self, other)
