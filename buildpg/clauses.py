from . import funcs, logic
from .components import Component, RawDangerous, yield_sep


class Clauses(Component):
    __slots__ = 'clauses'

    def __init__(self, *clauses):
        self.clauses = list(clauses)

    def render(self):
        yield from yield_sep(self.clauses, sep=RawDangerous('\n'))

    def __add__(self, other):
        self.clauses.append(other)
        return self


class Clause(Component):
    __slots__ = ('logic',)
    base = NotImplemented

    def __init__(self, logic):
        self.logic = logic

    def render(self):
        yield RawDangerous(self.base + ' ')
        yield self.logic

    def __add__(self, other):
        return Clauses(self, other)


def component_or_var(v):
    return v if isinstance(v, Component) else logic.Var(v)


class Select(Clause):
    base = 'SELECT'

    def __init__(self, select):
        if not isinstance(select, Component):
            select = logic.select_fields(*select)
        super().__init__(select)


class CommaClause(Clause):
    def __init__(self, *fields):
        super().__init__(funcs.comma_sep(*[component_or_var(f) for f in fields]))


class From(CommaClause):
    base = 'FROM'


class OrderBy(CommaClause):
    base = 'ORDER BY'


class Limit(Clause):
    base = 'LIMIT'

    def __init__(self, limit_value):
        super().__init__(limit_value)


class Join(Clause):
    base = 'JOIN'

    def __init__(self, table, on_clause=None):
        v = logic.as_var(table)
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


class Offset(Clause):
    base = 'OFFSET'

    def __init__(self, offset_value):
        super().__init__(offset_value)
