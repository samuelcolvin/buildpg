import re

from .components import BuildError, Component, Param

__all__ = (
    'render',
)


def render(sql, __open__='{{ ?', __close__=' ?}}', **ctx):
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

        if render:
            r = ''
            for chunk in render(var_name):
                if isinstance(chunk, Param):
                    r += add_param(chunk.value)
                else:
                    r += chunk
        else:
            r = add_param(v)
        return r

    var_regex = __open__ + r'?([\w_]+)(?:\.([\w_]+))?' + __close__
    query = re.sub(var_regex, repl, sql)
    return query, params
