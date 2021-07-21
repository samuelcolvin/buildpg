import sys
from textwrap import indent

from asyncpg import *  # noqa
from asyncpg.pool import Pool
from asyncpg.protocol import Record

from .main import render

try:
    import sqlparse
    from pygments import highlight
    from pygments.formatters import Terminal256Formatter
    from pygments.lexers.sql import PlPgsqlLexer
except ImportError:  # pragma: no cover
    sqlparse = None


class _BuildPgMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _format_sql(sql, formatted):
        if formatted and sqlparse is not None:
            sql = indent(sqlparse.format(str(sql), reindent=True), ' ' * 4)
            return highlight(sql, PlPgsqlLexer(), Terminal256Formatter(style='monokai')).strip('\n')
        else:
            return sql.strip('\r\n ')

    def _print_query(self, print_, sql, args):
        if print_:
            if not callable(print_):
                print_ = print
                formatted = sys.stdout.isatty()
            else:
                formatted = getattr(print_, 'formatted', False)
            print_(f'params: {args} query:\n{self._format_sql(sql, formatted)}')

    def print_b(self, query_template, *, print_=True, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return query, args

    async def execute_b(self, query_template, *, _timeout: float = None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return await self.execute(query, *args, timeout=_timeout)

    async def executemany_b(self, query_template, args, *, timeout: float = None, print_=False):
        query, _ = render(query_template, values=args[0])
        args_ = [render.get_params(a) for a in args]
        self._print_query(print_, query, args)
        return await self.executemany(query, args_, timeout=timeout)

    def cursor_b(self, query_template, *, _timeout: float = None, _prefetch=None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return self.cursor(query, *args, timeout=_timeout, prefetch=_prefetch)

    async def fetch_b(self, query_template, *, _timeout: float = None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return await self.fetch(query, *args, timeout=_timeout)

    async def fetchval_b(self, query_template, *, _timeout: float = None, _column=0, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return await self.fetchval(query, *args, timeout=_timeout, column=_column)

    async def fetchrow_b(self, query_template, *, _timeout: float = None, print_=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self._print_query(print_, query, args)
        return await self.fetchrow(query, *args, timeout=_timeout)


class BuildPgConnection(_BuildPgMixin, Connection):  # noqa
    pass


async def connect_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return await connect(*args, **kwargs)  # noqa


class BuildPgPool(_BuildPgMixin, Pool):
    pass


def create_pool_b(
    dsn=None,
    *,
    min_size=10,
    max_size=10,
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    setup=None,
    init=None,
    loop=None,
    connection_class=BuildPgConnection,
    record_class=Record,
    **connect_kwargs,
):
    """
    Create a connection pool.

    Can be used either with an ``async with`` block:

    Identical to ``asyncpg.create_pool`` except that both the pool and connection have the *_b varients of
    ``execute``, ``fetch``, ``fetchval``, ``fetchrow`` etc

    Arguments are exactly the same as ``asyncpg.create_pool``.
    """
    return BuildPgPool(
        dsn,
        connection_class=connection_class,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        loop=loop,
        setup=setup,
        init=init,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        record_class=record_class,
        **connect_kwargs,
    )
