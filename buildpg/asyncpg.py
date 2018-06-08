import logging

from asyncpg import *  # noqa

from .main import render

query_logger = logging.getLogger('buildpg.queries')


class BuildPgConnection(Connection):  # noqa
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_logging(query_logger)

    def setup_logging(self, logger):
        self.logger = logger
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        logger.addHandler(handler)

    def log_query(self, _log, query, args):
        if _log:
            self.logger.info('query:\n%s\nparams: %s', query, args)

    async def execute_b(self, query_template, _timeout: float=None, _log=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.log_query(_log, query, args)
        return await self.execute(query, *args, timeout=_timeout)

    async def executemany_b(self, query_template, args, timeout: float=None, _log=False):
        query, _ = render(query_template, values=args[0])
        args_ = [render.get_params(a) for a in args]
        self.log_query(_log, query, args)
        return await self.executemany(query, args_, timeout=timeout)

    def cursor_b(self, query_template, _timeout: float = None, _prefetch=None, _log=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.log_query(_log, query, args)
        return self.cursor(query, *args, timeout=_timeout, prefetch=_prefetch)

    async def fetch_b(self, query_template, _timeout: float=None, _log=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.log_query(_log, query, args)
        return await self.fetch(query, *args, timeout=_timeout)

    async def fetchval_b(self, query_template, _timeout: float=None, _column=0, _log=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.log_query(_log, query, args)
        return await self.fetchval(query, *args, timeout=_timeout, column=_column)

    async def fetchrow_b(self, query_template, _timeout: float=None, _log=False, **kwargs):
        query, args = render(query_template, **kwargs)
        self.log_query(_log, query, args)
        return await self.fetchrow(query, *args, timeout=_timeout)


async def connect_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return await connect(*args, **kwargs)  # noqa


def create_pool_b(*args, **kwargs):
    kwargs.setdefault('connection_class', BuildPgConnection)
    return create_pool(*args, **kwargs)  # noqa
