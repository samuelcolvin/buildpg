import pytest

from buildpg import S, SqlBlock, V, Var, funcs, render

args = 'template', 'var', 'expected_query', 'expected_params'
TESTS = [
    {
        'template': 'eq: {{ var }}',
        'var': lambda: S(1) > 2,
        'expected_query': 'eq: $1 > $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'and: {{ var }}',
        'var': lambda: S(1) & 2,
        'expected_query': 'and: $1 AND $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'or: {{ var }}',
        'var': lambda: S(1) | 2,
        'expected_query': 'or: $1 OR $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'inv: {{ var }}',
        'var': lambda: ~(S(1) % 2),
        'expected_query': 'inv: NOT($1 % $2)',
        'expected_params': [1, 2],
    },
    {
        'template': 'double inv: {{ var }}',
        'var': lambda: ~~(S(1) % 2),
        'expected_query': 'double inv: $1 % $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'eq: {{ var }}',
        'var': lambda: Var('foo') > 2,
        'expected_query': 'eq: foo > $1',
        'expected_params': [2],
    },
    {
        'template': 'chain: {{ var }}',
        'var': lambda: V('x') + 4 + 2 + 1,
        'expected_query': 'chain: x + $1 + $2 + $3',
        'expected_params': [4, 2, 1],
    },
    {
        'template': 'complex: {{ var }}',
        'var': lambda: (Var('foo') > 2) & ((SqlBlock('x') / 7 > 3) | (Var('another') ** 4 == 42)),
        'expected_query': 'complex: foo > $1 AND ($2 / $3 > $4 OR another ^ $5 = $6)',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
    {
        'template': 'complex AND OR: {{ var }}',
        # as above but using the AND and OR functions for clear usage
        'var': lambda: funcs.AND(V('foo') > 2, funcs.OR(S('x') / 7 > 3, V('another') ** 4 == 42)),
        'expected_query': 'complex AND OR: foo > $1 AND ($2 / $3 > $4 OR another ^ $5 = $6)',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
    {
        'template': 'inv chain: {{ var }}',
        'var': lambda: ~(V('x') == 2) | V('y'),
        'expected_query': 'inv chain: (NOT(x = $1)) OR y',
        'expected_params': [2],
    },
    {
        'template': 'func: {{ var }}',
        'var': lambda: funcs.upper(12),
        'expected_query': 'func: upper($1)',
        'expected_params': [12],
    },
    {
        'template': 'func args: {{ var }}',
        'var': lambda: funcs.left(V('x').cat('xx'), V('y') + 4 + 5),
        'expected_query': 'func args: left(x || $1, y + $2 + $3)',
        'expected_params': ['xx', 4, 5],
    },
    {
        'template': 'abs neg: {{ var }}',
        'var': lambda: funcs.abs(-S(4)),
        'expected_query': 'abs neg: @ -$1',
        'expected_params': [4],
    },
    {
        'template': 'abs brackets: {{ var }}',
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


@pytest.mark.parametrize('block,expected_query', [
    (lambda: SqlBlock(1) == 1, '$1 = $2'),
    (lambda: SqlBlock(1) != 1, '$1 != $2'),
    (lambda: SqlBlock(1) < 1, '$1 < $2'),
    (lambda: SqlBlock(1) <= 1, '$1 <= $2'),
    (lambda: SqlBlock(1) > 1, '$1 > $2'),
    (lambda: SqlBlock(1) + 1, '$1 + $2'),
    (lambda: SqlBlock(1) - 1, '$1 - $2'),
    (lambda: SqlBlock(1) * 1, '$1 * $2'),
    (lambda: SqlBlock(1) / 1, '$1 / $2'),
    (lambda: SqlBlock(1) % 1, '$1 % $2'),
    (lambda: SqlBlock(1) ** 1, '$1 ^ $2'),
    (lambda: V('x').contains(V('y')), 'x @> y'),
    (lambda: V('x').contained_by(V('y')), 'x <@ y'),
    (lambda: V('x').like('y'), 'x LIKE $1'),
    (lambda: V('x').cat('y'), 'x || $1'),
    (lambda: funcs.sqrt(4), '|/ $1'),
    (lambda: funcs.abs(4), '@ $1'),
    (lambda: funcs.factorial(4), '$1!'),
    (lambda: funcs.upper('a'), 'upper($1)'),
    (lambda: funcs.lower('a'), 'lower($1)'),
    (lambda: funcs.lower('a'), 'lower($1)'),
    (lambda: funcs.length('a'), 'length($1)'),
    (lambda: funcs.AND('a', 'b', 'c'), '$1 AND $2 AND $3'),
    (lambda: funcs.AND('a', 'b', V('c') | V('d')), '$1 AND $2 AND (c OR d)'),
    (lambda: funcs.OR('a', 'b', V('c') & V('d')), '$1 OR $2 OR c AND d'),
])
def test_simple_blocks(block, expected_query):
    query, _ = render('{{ v }}', v=block())
    assert expected_query == query


@pytest.mark.parametrize('block,s', [
    (lambda: SqlBlock(1) == 2, '<SqlBlock(1 = 2)>'),
    (lambda: SqlBlock('x') != 1, '<SqlBlock(x != 1)>'),
    (lambda: SqlBlock('y') < 2, '<SqlBlock(y < 2)>'),
])
def test_block_repr(block, s):
    assert s == repr(block())
