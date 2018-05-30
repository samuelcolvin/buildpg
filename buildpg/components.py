import re
from typing import Generator, Union

__all__ = (
    'Param',
    'Component',
    'BuildError',
    'RawDangerous',
    'Raw',
    'MultipleValues',
    'Values',
)

UNSAFE = re.compile('\W', flags=re.A)


class Param:
    __slots__ = 'value',

    def __init__(self, v):
        self.value = v


class Component:
    def render(self, name) -> Generator[Union[Param, str], None, None]:
        raise NotImplementedError()


class BuildError(RuntimeError):
    pass


class UnsafeError(RuntimeError):
    pass


class RawDangerous(Component):
    __slots__ = 'args',

    def __init__(self, *args):
        self.args = args

    def render(self, name):
        yield ', '.join(str(a) for a in self.args)


class Raw(RawDangerous):
    __slots__ = 'args',

    def __init__(self, *args):
        super().__init__(*args)
        if any(isinstance(a, str) and UNSAFE.search(a) for a in args):
            unsafe = [a for a in self.args if isinstance(a, str) and UNSAFE.search(a)]
            raise UnsafeError(f'raw arguments contain unsafe (non word) characters: {unsafe}')


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


class Blank(Component):
    """
    just substituted for $1, $2 etc., only used
    """


class Function(Component):
    pass


class upper(Function):
    pass
