from textwrap import indent

from asyncpg import *  # noqa

from .main import render

try:
    import sqlparse
    from pygments import highlight
    from pygments.lexers.sql import PlPgsqlLexer
    from pygments.formatters import Terminal256Formatter
except ImportError:  # pragma: no cover
    sqlparse = None


class BuildPgConnection(Connection):  # noqa
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def format_sql(sql):
        if sqlparse is not None:
            sql = indent(sqlparse.format(str(sql), reindent=True), ' ' * 4)
            return highlight(sql, PlPgsqlLexer(), Terminal256Formatter(style='monokai')).strip('\n')
        else:
            return sql.strip('\r\n ')

    def print_query(self, print_, sql, args):
        if print_:
            if not callable(print_):
                print_ = print
            print_(f'params: {args} query:\n{self.format_sql(sql)}')

    async def execute_b(self, query_template, _timeout: float=None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.print_query(print_, query, args)
        return await self.execute(query, *args, timeout=_timeout)

    async def executemany_b(self, query_template, args, timeout: float=None, print_=False):
        query, _ = render(query_template, values=args[0])
        args_ = [render.get_params(a) for a in args]
        self.print_query(print_, query, args)
        return await self.executemany(query, args_, timeout=timeout)

    def cursor_b(self, query_template, _timeout: float = None, _prefetch=None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.print_query(print_, query, args)
        return self.cursor(query, *args, timeout=_timeout, prefetch=_prefetch)

    async def fetch_b(self, query_template, _timeout: float=None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.print_query(print_, query, args)
        return await self.fetch(query, *args, timeout=_timeout)

    async def fetchval_b(self, query_template, _timeout: float=None, _column=0, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.print_query(print_, query, args)
        return await self.fetchval(query, *args, timeout=_timeout, column=_column)

    async def fetchrow_b(self, query_template, _timeout: float=None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.print_query(print_, query, args)
        return await self.fetchrow(query, *args, timeout=_timeout)


async def connect_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return await connect(*args, **kwargs)  # noqa


def create_pool_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return create_pool(*args, **kwargs)  # noqa
