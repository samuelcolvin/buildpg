import re
from functools import partial

from .components import BuildError, Component, ComponentError, Literal

__all__ = (
    'Renderer',
    'render',
)


class Renderer:
    def __init__(self, regex=r'(?<!:):([a-z][a-z\d_]*)', sep='__'):
        self.regex = re.compile(regex, flags=re.A)
        self.sep = sep

    def __call__(self, query_template, **ctx):
        params = []

        def add_param(p):
            params.append(p)
            return f'${len(params)}'

        repl = partial(self.replace, ctx=ctx, add_param=add_param)
        return self.regex.sub(repl, query_template), params

    def replace(self, m, *, ctx, add_param):
        var_name = m.group(1)
        if self.sep in var_name:
            var_name, extra_name = var_name.split(self.sep, 1)
        else:
            extra_name = None

        try:
            v = ctx[var_name]
        except KeyError:
            raise BuildError(f'variable "{var_name}" not found in context') from None

        try:
            render_gen = None
            if extra_name:
                render_gen = getattr(v, 'render_' + extra_name)
            elif isinstance(v, Component):
                render_gen = v.render

            if render_gen:
                return ''.join(self.add_chunk(render_gen(), add_param))
            else:
                return add_param(v)
        except ComponentError as exc:
            raise BuildError(f'"{var_name}": {exc}') from exc
        except Exception as exc:
            raise BuildError(f'"{var_name}": error building content, {exc.__class__.__name__}: {exc}') from exc

    @classmethod
    def add_chunk(cls, gen, add_param):
        for chunk in gen:
            if isinstance(chunk, Literal):
                yield chunk
            elif isinstance(chunk, Component):
                yield from cls.add_chunk(chunk.render(), add_param)
            else:
                yield add_param(chunk)

    def get_params(self, component: Component):
        return list(self._get_params(component.render()))

    @classmethod
    def _get_params(cls, gen):
        for chunk in gen:
            if isinstance(chunk, Component):
                yield from cls._get_params(chunk.render())
            elif not isinstance(chunk, Literal):
                yield chunk


render = Renderer()
