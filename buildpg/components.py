import re

__all__ = (
    'check_word',
    'BuildError',
    'ComponentError',
    'UnsafeError',
    'yield_sep',
    'Literal',
    'VarLiteral',
    'Component',
    'Select',
    'Values',
    'MultipleValues',
)

NOT_WORD = re.compile('[^\w.]', flags=re.A)


def check_word(s):
    if isinstance(s, int):
        s = str(s)
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
        return f'<{self.__class__.__name__}({self})>'


class KeyValueComponent:
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


class Values(KeyValueComponent, Component):
    def render(self):
        yield Literal('(')
        yield from yield_sep(self.values)
        yield Literal(')')

    def render_names(self):
        if not self.names:
            raise ComponentError(f'"names" are not available for nameless values')
        yield Literal(', '.join(self.names))


class Select(KeyValueComponent, Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        check_word_many(self.values)

    def render(self):
        if self.names:
            yield Literal(', '.join(f'{v} AS {n}' for v, n in zip(self.values, self.names)))
        else:
            yield Literal(', '.join(self.values))


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
