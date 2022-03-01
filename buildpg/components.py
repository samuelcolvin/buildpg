import re

__all__ = (
    'check_word',
    'BuildError',
    'ComponentError',
    'UnsafeError',
    'yield_sep',
    'RawDangerous',
    'VarLiteral',
    'Component',
    'Values',
    'MultipleValues',
    'SetValues',
    'JoinComponent',
)

NOT_WORD = re.compile(r'[^\w.*]', flags=re.A)


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


class UnsafeError(ComponentError):
    pass


class RawDangerous(str):
    pass


def yield_sep(iterable, sep=RawDangerous(', ')):
    iter_ = iter(iterable)
    yield next(iter_)
    for v in iter_:
        yield sep
        yield v


class VarLiteral(RawDangerous):
    def __init__(self, s: str):
        check_word(s)
        str.__init__(s)


class Component:
    def render(self):
        raise NotImplementedError()

    def __str__(self):
        return ''.join(self._get_chunks(self.render()))

    @classmethod
    def _get_chunks(cls, gen):
        for chunk in gen:
            if isinstance(chunk, Component):
                yield from cls._get_chunks(chunk.render())
            elif isinstance(chunk, str):
                yield chunk
            else:
                yield str(chunk)

    def __repr__(self):
        return f'<SQL: "{self}">'


class Values(Component):
    __slots__ = 'values', 'names'

    def __init__(self, *args, **kwargs):
        if (args and kwargs) or (not args and not kwargs):
            raise ValueError('either args or kwargs are required but not both')

        if args:
            self.names = None
            self.values = args
        else:
            self.names, self.values = zip(*kwargs.items())
            check_word_many(self.names)

    def render(self):
        yield RawDangerous('(')
        yield from yield_sep(self.values)
        yield RawDangerous(')')

    def render_names(self):
        if not self.names:
            raise ComponentError('"names" are not available for nameless values')
        yield RawDangerous(', '.join(self.names))


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


class SetValues(Component):
    __slots__ = ('kwargs',)

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @staticmethod
    def _yield_pairs(k, v):
        yield VarLiteral(k)
        yield RawDangerous(' = ')
        yield v

    def render(self):
        iter_ = iter(self.kwargs.items())
        yield from self._yield_pairs(*next(iter_))
        for k, v in iter_:
            yield RawDangerous(', ')
            yield from self._yield_pairs(k, v)


class JoinComponent(Component):
    __slots__ = 'sep', 'items'

    def __init__(self, items, sep=RawDangerous(', ')):
        self.items = items
        self.sep = sep

    def render(self):
        yield from yield_sep(self.items, self.sep)
