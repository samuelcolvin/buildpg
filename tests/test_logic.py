import pytest

from buildpg import Empty, Func, RawDangerous, S, SqlBlock, V, Var, funcs, render, select_fields

args = 'template', 'var', 'expected_query', 'expected_params'
TESTS = [
    {'template': 'eq: :var', 'var': lambda: S(1) > 2, 'expected_query': 'eq: $1 > $2', 'expected_params': [1, 2]},
    {'template': 'and: :var', 'var': lambda: S(1) & 2, 'expected_query': 'and: $1 AND $2', 'expected_params': [1, 2]},
    {'template': 'or: :var', 'var': lambda: S(1) | 2, 'expected_query': 'or: $1 OR $2', 'expected_params': [1, 2]},
    {
        'template': 'inv: :var',
        'var': lambda: ~(S(1) % 2),
        'expected_query': 'inv: not($1 % $2)',
        'expected_params': [1, 2],
    },
    {
        'template': 'double inv: :var',
        'var': lambda: ~~(S(1) % 2),
        'expected_query': 'double inv: $1 % $2',
        'expected_params': [1, 2],
    },
    {'template': 'eq: :var', 'var': lambda: Var('foo') > 2, 'expected_query': 'eq: foo > $1', 'expected_params': [2]},
    {
        'template': 'chain: :var',
        'var': lambda: V('x') + 4 + 2 + 1,
        'expected_query': 'chain: x + $1 + $2 + $3',
        'expected_params': [4, 2, 1],
    },
    {
        'template': 'complex: :var',
        'var': lambda: (Var('foo') > 2) & ((SqlBlock('x') / 7 > 3) | (Var('another') ** 4 == 42)),
        'expected_query': 'complex: foo > $1 AND ($2 / $3 > $4 OR another ^ $5 = $6)',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
    {
        'template': 'complex AND OR: :var',
        # as above but using the AND and OR functions for clear usage
        'var': lambda: funcs.AND(V('foo') > 2, funcs.OR(S('x') / 7 > 3, V('another') ** 4 == 42)),
        'expected_query': 'complex AND OR: foo > $1 AND ($2 / $3 > $4 OR another ^ $5 = $6)',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
    {
        'template': 'inv chain: :var',
        'var': lambda: ~(V('x') == 2) | V('y'),
        'expected_query': 'inv chain: not(x = $1) OR y',
        'expected_params': [2],
    },
    {
        'template': 'func: :var',
        'var': lambda: funcs.upper(12),
        'expected_query': 'func: upper($1)',
        'expected_params': [12],
    },
    {
        'template': 'func args: :var',
        'var': lambda: funcs.left(V('x').cat('xx'), V('y') + 4 + 5),
        'expected_query': 'func args: left(x || $1, y + $2 + $3)',
        'expected_params': ['xx', 4, 5],
    },
    {
        'template': 'abs neg: :var',
        'var': lambda: funcs.abs(-S(4)),
        'expected_query': 'abs neg: @ -$1',
        'expected_params': [4],
    },
    {
        'template': 'abs brackets: :var',
        'var': lambda: funcs.abs(S(4) + S(5)),
        'expected_query': 'abs brackets: @ ($1 + $2)',
        'expected_params': [4, 5],
    },
]


@pytest.mark.parametrize(','.join(args), [[t[a] for a in args] for t in TESTS], ids=[t['template'] for t in TESTS])
def test_render(template, var, expected_query, expected_params):
    query, params = render(template, var=var())
    assert expected_query == query
    assert expected_params == params


@pytest.mark.parametrize(
    'block,expected_query',
    [
        (lambda: SqlBlock(1) == 2, '$1 = $2'),
        (lambda: SqlBlock(1) != 2, '$1 != $2'),
        (lambda: SqlBlock(1) < 2, '$1 < $2'),
        (lambda: SqlBlock(1) <= 2, '$1 <= $2'),
        (lambda: SqlBlock(1) > 2, '$1 > $2'),
        (lambda: SqlBlock(1) >= 2, '$1 >= $2'),
        (lambda: SqlBlock(1) + 2, '$1 + $2'),
        (lambda: SqlBlock(1) - 2, '$1 - $2'),
        (lambda: SqlBlock(1) * 2, '$1 * $2'),
        (lambda: SqlBlock(1) / 2, '$1 / $2'),
        (lambda: SqlBlock(1) % 2, '$1 % $2'),
        (lambda: SqlBlock(1) ** 2, '$1 ^ $2'),
        (lambda: V('x').contains(V('y')), 'x @> y'),
        (lambda: V('x').overlap(V('y')), 'x && y'),
        (lambda: V('x').contained_by(V('y')), 'x <@ y'),
        (lambda: V('x').like('y'), 'x LIKE $1'),
        (lambda: V('x').ilike('y'), 'x ILIKE $1'),
        (lambda: V('x').cat('y'), 'x || $1'),
        (lambda: V('x').comma(V('y')), 'x, y'),
        (lambda: V('a').asc(), 'a ASC'),
        (lambda: V('a').desc(), 'a DESC'),
        (lambda: ~V('a'), 'not(a)'),
        (lambda: -V('a'), '-a'),
        (lambda: V('x').operate(RawDangerous(' foobar '), V('y')), 'x foobar y'),
        (lambda: funcs.sqrt(4), '|/ $1'),
        (lambda: funcs.abs(4), '@ $1'),
        (lambda: funcs.factorial(4), '$1!'),
        (lambda: funcs.count('*'), 'COUNT(*)'),
        (lambda: funcs.count(V('*')), 'COUNT(*)'),
        (lambda: funcs.count('*').as_('foobar'), 'COUNT(*) AS foobar'),
        (lambda: funcs.upper('a'), 'upper($1)'),
        (lambda: funcs.lower('a'), 'lower($1)'),
        (lambda: funcs.lower('a') > 4, 'lower($1) > $2'),
        (lambda: funcs.length('a'), 'length($1)'),
        (lambda: funcs.position('a', 'b'), 'position($1 in $2)'),
        (lambda: funcs.substring('a', 'b'), 'substring($1 from $2)'),
        (lambda: funcs.substring('x', 2, 3), 'substring($1 from $2 for $3)'),
        (lambda: funcs.extract(V('epoch').from_(V('foo.bar'))).cast('int'), 'extract(epoch from foo.bar)::int'),
        (lambda: funcs.AND('a', 'b', 'c'), '$1 AND $2 AND $3'),
        (lambda: funcs.AND('a', 'b', V('c') | V('d')), '$1 AND $2 AND (c OR d)'),
        (lambda: funcs.OR('a', 'b', V('c') & V('d')), '$1 OR $2 OR c AND d'),
        (lambda: funcs.comma_sep('a', 'b', V('c') | V('d')), '$1, $2, c OR d'),
        (lambda: funcs.comma_sep(V('first_name'), 123), 'first_name, $1'),
        (lambda: Func('foobar', V('x'), V('y')), 'foobar(x, y)'),
        (lambda: Func('foobar', funcs.comma_sep('x', 'y')), 'foobar($1, $2)'),
        (lambda: Empty() & (V('foo') == 4), ' AND foo = $1'),
        (lambda: Empty() & (V('bar') == 4), ' AND bar = $1'),
        (lambda: V('epoch').at_time_zone('MST'), 'epoch AT TIME ZONE $1'),
        (lambda: S('2032-02-16 19:38:40-08').at_time_zone('MST'), '$1 AT TIME ZONE $2'),
        (lambda: V('foo').matches(V('bar')), 'foo @@ bar'),
        (lambda: V('foo').is_(V('bar')), 'foo is bar'),
        (lambda: V('foo').is_not(V('bar')), 'foo is not bar'),
        (
            lambda: funcs.to_tsvector('fat cats ate rats').matches(funcs.to_tsquery('cat & rat')),
            'to_tsvector($1) @@ to_tsquery($2)',
        ),
        (lambda: funcs.now(), 'now()'),
        (lambda: select_fields('foo', 'bar'), 'foo, bar'),
        (lambda: select_fields('foo', S(RawDangerous("'raw text'"))), "foo, 'raw text'"),
        (lambda: funcs.NOT(V('a').in_([1, 2])), 'not(a in $1)'),
        (lambda: ~V('a').in_([1, 2]), 'not(a in $1)'),
        (lambda: funcs.NOT(V('a') == funcs.any([1, 2])), 'not(a = any($1))'),
    ],
)
def test_simple_blocks(block, expected_query):
    query, _ = render(':v', v=block())
    assert expected_query == query


@pytest.mark.parametrize(
    'block,s',
    [
        (lambda: SqlBlock(1) == 2, '<SQL: "1 = 2">'),
        (lambda: SqlBlock('x') != 1, '<SQL: "x != 1">'),
        (lambda: SqlBlock('y') < 2, '<SQL: "y < 2">'),
    ],
)
def test_block_repr(block, s):
    assert s == repr(block())
