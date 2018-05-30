from typing import Generator, Union

__all__ = (
    'Param',
    'Component',
    'BuildError',
    'Raw',
    'MultipleValues',
    'Values',
)


class Param:
    __slots__ = 'value',

    def __init__(self, v):
        self.value = v


class Component:
    def render(self, name) -> Generator[Union[Param, str], None, None]:
        raise NotImplementedError()


class BuildError(RuntimeError):
    pass


class Raw(Component):
    """
    used for one or more raw values, eg. fields to select
    rendered with
    """
    __slots__ = 'args',

    def __init__(self, *args):
        self.args = args

    def render(self, name):
        yield ', '.join(str(a) for a in self.args)


def _yield_sep(iter, sep=', ', yield_from=False):
    mid = 0
    for v in iter:
        if mid:
            yield sep
        mid = 1
        if yield_from:
            yield from v
        else:
            yield v


class Values(Component):
    """
    can be rendered with {{ v }}
    names can be rendered with {{ v.names }}

    For multiple rows use Values(Values(...), Values(...)) or append_row
    """
    __slots__ = 'values', 'names'

    def __init__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError('either args or kwargs are required but not both')

        if not args and not kwargs:
            raise ValueError('args or kwargs are required')

        if args:
            self.names = None
            self.values = args
        else:
            self.names, self.values = zip(*kwargs.items())

    def render(self, name):
        yield '('
        yield from _yield_sep(map(Param, self.values))
        yield ')'

    def render_names(self, name):
        if not self.names:
            raise BuildError(f'{name}: "names" are not available for nameless values')
        yield ', '.join(self.names)


class MultipleValues(Component):
    __slots__ = 'values', 'names'

    def __init__(self, *args):
        first = args[0]
        self.names = first.names
        self.render_names = first.render_names
        self.rows = [first]
        expected_len = len(first.values)
        for r in args[1:]:
            if not isinstance(r, Values):
                raise ValueError('either all or no arguments should be Values()')
            if r.names != self.names:
                raise ValueError(f'names of different rows do not match {r.names} != {self.names}')
            if not self.names and len(r.values) != expected_len:
                raise ValueError(f"row lengths don't match {r.values} != {expected_len}")
            self.rows.append(r)

    def render(self, name):
        yield from _yield_sep((row.render(name) for row in self.rows), yield_from=True)


class Logic(Component):
    """
    used for building logic, should implement lt, gl, eq etc,

    used as in
    foo = l('hello') > 4

    will also required and_(*<fields>) and or_(*<fields>)
    """

    def __gt__(self, other):
        # debug(self, other)
        return Logic(other)

    def __lt__(self, other):
        # debug(self, other)
        return Logic(other)

    def __and__(self, other):
        # debug(self, other)
        return Logic(other)

    def __or__(self, other):
        return Logic(other)

    def __invert__(self):
        return Logic('bool')

    def __repr__(self):
        return f'<Logic({", ".join(repr(v) for v in self.args)})>'


class Blank(Component):
    """
    just substituted for $1, $2 etc., only used
    """


class Function(Component):
    pass


class upper(Function):
    pass
