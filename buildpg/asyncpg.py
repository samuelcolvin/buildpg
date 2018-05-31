from asyncpg import *  # noqa

from .main import render


class BuildPgConnection(Connection):  # noqa
    async def execute_b(self, query_template, __timeout: float=None, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.execute(query, *args, timeout=__timeout)

    async def executemany_b(self, query_template, __timeout: float=None, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.executemany(query, *args, timeout=__timeout)

    async def cursor_b(self, query_template, __timeout: float = None, __prefetch=None, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.cursor(query, *args, timeout=__timeout, prefetch=__prefetch)

    # TODO prepare

    async def fetch_b(self, query_template, __timeout: float=None, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.fetch(query, *args, timeout=__timeout)

    async def fetchval_b(self, query_template, __timeout: float=None, __column=0, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.fetchval(query, *args, timeout=__timeout, column=__column)

    async def fetchrow_b(self, query_template, __timeout: float=None, **kwargs):
        query, args = render(query_template, **kwargs)
        return await self.fetchrow(query, *args, timeout=__timeout)


async def connect_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return await connect(*args, **kwargs)  # noqa


async def create_pool_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return await create_pool(*args, **kwargs)  # noqa
