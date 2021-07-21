from datetime import datetime

import pytest

from buildpg import MultipleValues, S, V, Values, asyncpg, funcs, render, select_fields

from .conftest import DB_NAME

pytestmark = pytest.mark.asyncio


async def test_manual_select(conn):
    query, params = render('SELECT :v FROM users ORDER BY first_name', v=select_fields('first_name', 'last_name'))
    v = await conn.fetch(query, *params)
    assert [
        {'first_name': 'Franks', 'last_name': 'spencer'},
        {'first_name': 'Fred', 'last_name': 'blogs'},
        {'first_name': 'Joe', 'last_name': None},
    ] == [dict(r) for r in v]


async def test_manual_logic(conn):
    query, params = render(
        'SELECT :select FROM users WHERE :where ORDER BY :order_by',
        select=select_fields('first_name'),
        where=V('created') > datetime(2021, 1, 1),
        order_by=V('last_name'),
    )
    v = await conn.fetch(query, *params)
    assert ['Fred', 'Joe'] == [r[0] for r in v]


async def test_logic(conn, capsys):
    a, b, c, d = await conn.fetchrow_b(
        'SELECT :a, :b, :c, :d::int', a=funcs.cast(5, 'int') * 5, b=funcs.sqrt(676), c=S('a').cat('b'), d=987_654
    )
    assert a == 25
    assert b == 26
    assert c == 'ab'
    assert d == 987_654
    assert 'SELECT' not in capsys.readouterr().out


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
    async for r in conn.cursor_b(q, s=select_fields('first_name'), o=V('first_name').asc()):
        results.append(tuple(r))
        if len(results) == 2:
            break
    assert results == [('Franks',), ('Fred',)]


async def test_pool():
    async with asyncpg.create_pool_b(f'postgresql://postgres@localhost/{DB_NAME}') as pool:
        async with pool.acquire() as conn:
            v = await conn.fetchval_b('SELECT :v FROM users ORDER BY id LIMIT 1', v=funcs.right(V('first_name'), 3))

    assert v == 'red'


async def test_log(conn, capsys):
    a = await conn.fetchval_b('SELECT :a', print_=True, __timeout=12, a=funcs.cast(5, 'int') * 5)
    assert a == 25

    assert 'SELECT' in capsys.readouterr().out


async def test_print(conn, capsys):
    query, params = conn.print_b('SELECT :a', a=funcs.cast(5, 'int') * 5)
    assert query == 'SELECT $1::int * $2'
    assert params == [5, 5]

    assert 'SELECT' in capsys.readouterr().out


async def test_log_callable(conn):
    logged_message = None

    def foobar(arg):
        nonlocal logged_message
        logged_message = arg

    a = await conn.fetchval_b('SELECT :a', print_=foobar, __timeout=12, a=funcs.cast(5, 'int') * 5)
    assert a == 25

    assert 'SELECT' in logged_message


async def test_coloured_callable(conn):
    logged_message = None

    def foobar(arg):
        nonlocal logged_message
        logged_message = arg

    foobar.formatted = True
    a = await conn.fetchval_b('SELECT :a', print_=foobar, __timeout=12, a=funcs.cast(5, 'int') * 5)
    assert a == 25

    assert 'SELECT' in logged_message
    assert '\x1b[' in logged_message


async def test_pool_fetch():
    async with asyncpg.create_pool_b(f'postgresql://postgres@localhost/{DB_NAME}') as pool:
        v = await pool.fetchval_b('SELECT :v FROM users ORDER BY id LIMIT 1', v=funcs.right(V('first_name'), 3))

    assert v == 'red'
