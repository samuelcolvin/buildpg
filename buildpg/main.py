import re

from .components import BuildError, Component, Param

__all__ = (
    'render',
)


def render(query_template, __open__='{{ ?', __close__=' ?}}', **ctx):
    params = []

    def add_param(p):
        params.append(p)
        return f'${len(params)}'

    def repl(m):
        var_name, extra_name = m.groups()
        try:
            v = ctx[var_name]
        except KeyError:
            raise BuildError(f'variable "{var_name}" not found in context') from None

        render = None
        if extra_name:
            try:
                render = getattr(v, 'render_' + extra_name)
            except AttributeError:
                raise BuildError(f'"{var_name}": extra renderer "{extra_name}" not found')
        elif isinstance(v, Component):
            render = v.render

        try:
            r = ''

            def add_chunk(chunk):
                nonlocal r
                if isinstance(chunk, Param):
                    r += add_param(chunk.value)
                elif isinstance(chunk, Component):
                    for chunk_ in chunk.render(var_name):
                        add_chunk(chunk_)
                else:
                    r += chunk

            if render:
                for chunk in render(var_name):
                    add_chunk(chunk)
            else:
                r = add_param(v)
            return r
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(f'error building content for "{var_name}"') from exc

    var_regex = __open__ + r'?(\w+)(?:\.(\w+))?' + __close__
    query = re.sub(var_regex, repl, query_template, flags=re.A)
    return query, params
