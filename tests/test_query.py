from datetime import datetime

from buildpg import MultipleValues, S, SelectFields, V, Values, asyncpg, funcs, render

from .conftest import DB_NAME


async def test_manual_select(conn):
    query, params = render('SELECT :v FROM users ORDER BY first_name', v=SelectFields('first_name', 'last_name'))
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
        'SELECT :select FROM users WHERE :where ORDER BY :order_by',
        select=SelectFields('first_name'),
        where=V('created') > datetime(2021, 1, 1),
        order_by=V('last_name'),
    )
    v = await conn.fetch(query, *params)
    assert ['Fred', 'Joe'] == [r[0] for r in v]


async def test_logic(conn):
    a, b, c, d = await conn.fetchrow_b('SELECT :a, :b, :c, :d::int',
                                       a=funcs.cast(5, 'int') * 5, b=funcs.sqrt(676), c=S('a').cat('b'), d=987654)
    assert a == 25
    assert b == 26
    assert c == 'ab'
    assert d == 987654


async def test_multiple_values_execute(conn):
    co_id = await conn.fetchval('SELECT id FROM companies')
    v = MultipleValues(
        Values(company=co_id, first_name='anne', last_name=None, value=3, created=datetime(2032, 1, 1)),
        Values(company=co_id, first_name='ben', last_name='better', value=5, created=datetime(2032, 1, 2)),
        Values(company=co_id, first_name='charlie', last_name='cat', value=5, created=V('DEFAULT')),
    )
    await conn.execute_b('INSERT INTO users (:values__names) VALUES :values', values=v)
    assert 6 == await conn.fetchval('SELECT COUNT(*) FROM users')


async def test_values_executemany(conn):
    co_id = await conn.fetchval('SELECT id FROM companies')
    v = [
        Values(company=co_id, first_name='anne', last_name=None, value=3, created=datetime(2032, 1, 1)),
        Values(company=co_id, first_name='ben', last_name='better', value=5, created=datetime(2032, 1, 2)),
        Values(company=co_id, first_name='charlie', last_name='cat', value=5, created=datetime(2032, 1, 3)),
    ]
    await conn.executemany_b('INSERT INTO users (:values__names) VALUES :values', v)
    assert 6 == await conn.fetchval('SELECT COUNT(*) FROM users')


async def test_values_executemany_default(conn):
    co_id = await conn.fetchval('SELECT id FROM companies')
    v = [
        Values(company=co_id, first_name='anne', last_name=None, value=V('DEFAULT')),
        Values(company=co_id, first_name='ben', last_name='better', value=V('DEFAULT')),
        Values(company=co_id, first_name='charlie', last_name='cat', value=V('DEFAULT')),
    ]
    await conn.executemany_b('INSERT INTO users (:values__names) VALUES :values', v)
    assert 6 == await conn.fetchval('SELECT COUNT(*) FROM users')


async def test_position(conn):
    result = await conn.fetch_b('SELECT :a', a=funcs.position('xx', 'testing xx more'))
    assert [dict(r) for r in result] == [{'position': 9}]


async def test_substring(conn):
    a = await conn.fetchval_b('SELECT :a', a=funcs.substring('Samuel', '...$'))
    assert a == 'uel'


async def test_substring_for(conn):
    a = await conn.fetchval_b('SELECT :a', a=funcs.substring('Samuel', funcs.cast(2, 'int'), funcs.cast(3, 'int')))
    assert a == 'amu'


async def test_cursor(conn):
    results = []
    q = 'SELECT :s FROM users ORDER BY :o'
    async for r in conn.cursor_b(q, s=SelectFields('first_name'), o=V('first_name').asc()):
        results.append(tuple(r))
        if len(results) == 2:
            break
    assert results == [('Franks',), ('Fred',)]


async def test_pool():
    async with asyncpg.create_pool_b(f'postgresql://postgres@localhost/{DB_NAME}') as pool:
        async with pool.acquire() as conn:
            v = await conn.fetchval_b('SELECT :v FROM users ORDER BY id LIMIT 1', v=funcs.right(V('first_name'), 3))

    assert v == 'red'
