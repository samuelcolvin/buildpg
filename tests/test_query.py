from datetime import datetime

from buildpg import Select, Var, render


async def test_select(conn):
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


async def test_logic(conn):
    query, params = render(
        'SELECT {{select}} FROM users WHERE {{where}} ORDER BY {{order_by}}',
        select=Select('first_name'),
        where=Var('created') > datetime(2021, 1, 1),
        order_by=Var('last_name'),
    )
    v = await conn.fetch(query, *params)
    assert ['Fred', 'Joe'] == [r[0] for r in v]
