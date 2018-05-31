import re

__all__ = (
    'check_word',
    'BuildError',
    'UnsafeError',
    'yield_sep',
    'Literal',
    'VarLiteral',
    'Component',
    'RawDangerous',
    'Raw',
    'MultipleValues',
    'Values',
)

NOT_WORD = re.compile('\W', flags=re.A)


def check_word(s):
    if not isinstance(s, str):
        raise TypeError('value is not a string')
    if NOT_WORD.search(s):
        raise UnsafeError(f'str contain unsafe (non word) characters: "{s}"')


def check_word_many(args):
    if any(not isinstance(a, str) or NOT_WORD.search(a) for a in args):
        unsafe = [a for a in args if not isinstance(a, str) or NOT_WORD.search(a)]
        raise UnsafeError(f'raw arguments contain unsafe (non word) characters: {unsafe}')


class BuildError(RuntimeError):
    pass


class ComponentError(BuildError):
    pass


class UnsafeError(RuntimeError):
    pass


class Literal(str):
    pass


def yield_sep(iterable, sep=Literal(', ')):
    iter_ = iter(iterable)
    yield next(iter_)
    for v in iter_:
        yield sep
        yield v


class VarLiteral(Literal):
    def __init__(self, s: str):
        check_word(s)
        str.__init__(s)


class Component:
    def render(self):
        raise NotImplementedError()

    def __str__(self):
        chunks = []

        def add_chunk(chunk):
            if isinstance(chunk, Component):
                for chunk_ in chunk.render():
                    add_chunk(chunk_)
            elif isinstance(chunk, str):
                chunks.append(chunk)
            else:
                chunks.append(str(chunk))

        for chunk in self.render():
            add_chunk(chunk)

        return ''.join(chunks)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self})>'


class RawDangerous(Component):
    __slots__ = 'args',

    def __init__(self, *args):
        self.args = args

    def render(self):
        yield Literal(', '.join(str(a) for a in self.args))


class Raw(RawDangerous):
    __slots__ = 'args',

    def __init__(self, *args):
        check_word_many(args)
        super().__init__(*args)


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
            check_word_many(self.names)

    def render(self):
        yield Literal('(')
        yield from yield_sep(self.values)
        yield Literal(')')

    def render_names(self):
        if not self.names:
            raise ComponentError(f'"names" are not available for nameless values')
        yield Literal(', '.join(self.names))


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

    def render(self):
        yield from yield_sep(self.rows)
