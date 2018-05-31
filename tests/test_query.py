from datetime import datetime

from buildpg import S, Select, V, funcs, render


async def test_manual_select(conn):
    query, params = render('SELECT {{v}} FROM users ORDER BY first_name', v=Select('first_name', 'last_name'))
    v = await conn.fetch(query, *params)
    assert [
        {
            'first_name': 'Franks',
            'last_name': 'spencer',
        },
        {
            'first_name': 'Fred',
            'last_name': 'blogs',
        },
        {
            'first_name': 'Joe',
            'last_name': None,
        },
    ] == [dict(r) for r in v]


async def test_manual_logic(conn):
    query, params = render(
        'SELECT {{select}} FROM users WHERE {{where}} ORDER BY {{order_by}}',
        select=Select('first_name'),
        where=V('created') > datetime(2021, 1, 1),
        order_by=V('last_name'),
    )
    v = await conn.fetch(query, *params)
    assert ['Fred', 'Joe'] == [r[0] for r in v]


async def test_fetchrow(conn):
    a, b, c, d = await conn.fetchrow_b('SELECT {{a}}, {{b}}, {{c}}, {{d}}::int',
                                       a=funcs.cast(5, 'int') * 5, b=funcs.sqrt(676), c=S('a').cat('b'), d=987654)
    assert a == 25
    assert b == 26
    assert c == 'ab'
    assert d == 987654
