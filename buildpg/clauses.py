from . import funcs, logic
from .components import Component, Literal, yield_sep


class Clauses(Component):
    __slots__ = 'clauses'

    def __init__(self, *clauses):
        self.clauses = list(clauses)

    def render(self):
        yield from yield_sep(self.clauses, sep=Literal('\n'))

    def __add__(self, other):
        self.clauses.append(other)
        return self


class Clause(Component):
    __slots__ = 'logic',
    base = NotImplemented

    def __init__(self, logic_block):
        if not isinstance(logic_block, Component):
            raise TypeError('Clause logic_block should be a Component')
        self.logic_block = logic_block

    def render(self):
        yield Literal(self.base + ' ')
        yield self.logic_block

    def __add__(self, other):
        return Clauses(self, other)


def component_or_var(v):
    return v if isinstance(v, Component) else logic.Var(v)


class CommaClause(Clause):
    def __init__(self, *tables):
        super().__init__(funcs.comma_sep(*[component_or_var(t) for t in tables]))


class From(CommaClause):
    base = 'FROM'


class OrderBy(CommaClause):
    base = 'ORDER BY'


class Limit(CommaClause):
    base = 'LIMIT'


class Join(Clause):
    base = 'JOIN'

    def __init__(self, table, on_clause=None):
        v = logic.Var(table)
        if on_clause:
            v = v.on(on_clause)
        super().__init__(v)


class LeftJoin(Join):
    base = 'LEFT JOIN'


class RightJoin(Join):
    base = 'RIGHT JOIN'


class FullJoin(Join):
    base = 'FULL JOIN'


class CrossJoin(Join):
    base = 'CROSS JOIN'


class Where(Clause):
    base = 'WHERE'
