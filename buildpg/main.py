import re
from functools import partial

from .components import BuildError, Component, ComponentError, Literal

__all__ = (
    'Renderer',
    'render',
)


class Renderer:
    def __init__(self, open='{{ ?', close=' ?}}'):
        self.var_regex = re.compile(open + r'?(\w+)(?:\.(\w+))?' + close, flags=re.A)

    def __call__(self, query_template, **ctx):
        params = []

        def add_param(p):
            params.append(p)
            return f'${len(params)}'

        repl = partial(self.replace, ctx=ctx, add_param=add_param)
        return self.var_regex.sub(repl, query_template), params

    @classmethod
    def replace(cls, m, *, ctx, add_param):  # noqa: C901 (ignore complexity)
        var_name, extra_name = m.groups()
        try:
            v = ctx[var_name]
        except KeyError:
            raise BuildError(f'variable "{var_name}" not found in context') from None

        render_gen = None
        if extra_name:
            try:
                render_gen = getattr(v, 'render_' + extra_name)
            except AttributeError:
                raise BuildError(f'"{var_name}": extra renderer "{extra_name}" not found')
        elif isinstance(v, Component):
            render_gen = v.render

        chunks = []

        def add_chunk(chunk):
            if isinstance(chunk, Literal):
                chunks.append(chunk)
            elif isinstance(chunk, Component):
                for chunk_ in chunk.render():
                    add_chunk(chunk_)
            else:
                chunks.append(add_param(chunk))

        try:
            if render_gen:
                for chunk in render_gen():
                    add_chunk(chunk)
                return ''.join(chunks)
            else:
                return add_param(v)
        except ComponentError as exc:
            raise BuildError(f'"{var_name}": {exc}') from exc
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(f'"{var_name}": error building content') from exc


render = Renderer()
