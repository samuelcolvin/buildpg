import pytest
from buildpg import SqlBlock, S, Var, V, render
from buildpg import funcs


args = 'template', 'var', 'expected_query', 'expected_params'
TESTS = [
    {
        'template': 'eq: {{ var }}',
        'var': S(1) > 2,
        'expected_query': 'eq: $1 > $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'and: {{ var }}',
        'var': S(1) & 2,
        'expected_query': 'and: $1 AND $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'or: {{ var }}',
        'var': S(1) | 2,
        'expected_query': 'or: $1 OR $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'inv: {{ var }}',
        'var': ~(S(1) % 2),
        'expected_query': 'inv: NOT($1 % $2)',
        'expected_params': [1, 2],
    },
    {
        'template': 'double inv: {{ var }}',
        'var': ~~(S(1) % 2),
        'expected_query': 'double inv: $1 % $2',
        'expected_params': [1, 2],
    },
    {
        'template': 'eq: {{ var }}',
        'var': Var('foo') > 2,
        'expected_query': 'eq: foo > $1',
        'expected_params': [2],
    },
    {
        'template': 'chain: {{ var }}',
        'var': V('x') + 4 + 2 + 1,
        'expected_query': 'chain: x + $1 + $2 + $3',
        'expected_params': [4, 2, 1],
    },
    {
        'template': 'complex: {{ var }}',
        'var': (Var('foo') > 2) & ((S('x') / 7 > 3) | (Var('another') ** 4 == 42)),
        'expected_query': 'complex: (foo > $1) AND (($2 / $3) > $4) OR (another ^ $5) = $6',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
    {
        'template': 'inv chain: {{ var }}',
        'var': ~(V('x') == 2) | V('y'),
        'expected_query': 'inv chain: (NOT(x = $1)) OR y',
        'expected_params': [2],
    },
    {
        'template': 'func: {{ var }}',
        'var': funcs.upper(12),
        'expected_query': 'func: upper($1)',
        'expected_params': [12],
    },
    {
        'template': 'func args: {{ var }}',
        'var': funcs.left(V('x').cat('xx'), V('y') + 4 + 5),
        'expected_query': 'func args: left(x || $1, y + $2 + $3)',
        'expected_params': ['xx', 4, 5],
    },
    {
        'template': 'abs neg: {{ var }}',
        'var': funcs.abs(-S(4)),
        'expected_query': 'abs neg: @ -$1',
        'expected_params': [4],
    },
    {
        'template': 'abs brackets: {{ var }}',
        'var': funcs.abs(S(4) + S(5)),
        'expected_query': 'abs brackets: @ ($1 + $2)',
        'expected_params': [4, 5],
    },
]


@pytest.mark.parametrize(','.join(args), [[t[a] for a in args] for t in TESTS], ids=[t['template'] for t in TESTS])
def test_render(template, var, expected_query, expected_params):
    query, params = render(template, var=var)
    assert expected_query == query
    assert expected_params == params


@pytest.mark.parametrize('block,expected_query', [
    (SqlBlock(1) == 1, '$1 = $2'),
    (SqlBlock(1) != 1, '$1 != $2'),
    (SqlBlock(1) < 1, '$1 < $2'),
    (SqlBlock(1) <= 1, '$1 <= $2'),
    (SqlBlock(1) > 1, '$1 > $2'),
    (SqlBlock(1) + 1, '$1 + $2'),
    (SqlBlock(1) - 1, '$1 - $2'),
    (SqlBlock(1) * 1, '$1 * $2'),
    (SqlBlock(1) / 1, '$1 / $2'),
    (SqlBlock(1) % 1, '$1 % $2'),
    (SqlBlock(1) ** 1, '$1 ^ $2'),
    (V('x').contains(V('y')), 'x @> y'),
    (V('x').contained_by(V('y')), 'x <@ y'),
    (V('x').like('y'), 'x LIKE $1'),
    (V('x').cat('y'), 'x || $1'),
    (funcs.sqrt(4), '|/ $1'),
    (funcs.abs(4), '@ $1'),
    (funcs.factorial(4), '$1 ! '),
    (funcs.upper('a'), 'upper($1)'),
    (funcs.lower('a'), 'lower($1)'),
    (funcs.lower('a'), 'lower($1)'),
    (funcs.length('a'), 'length($1)'),
])
def test_simple_blocks(block, expected_query):
    query, _ = render('{{ v }}', v=block)
    assert expected_query == query


@pytest.mark.parametrize('block,s', [
    (SqlBlock(1) == 2, '<SqlBlock(1 = 2)>'),
    (SqlBlock('x') != 1, '<SqlBlock(x != 1)>'),
    (SqlBlock('y') < 2, '<SqlBlock(y < 2)>'),
])
def test_block_repr(block, s):
    assert s == repr(block)
