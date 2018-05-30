import pytest
from buildpg import SqlBlock, S, Var, V, render


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
        'var': ~S(1) % 2,
        'expected_query': 'inv: NOT ($1 % $2)',
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
        'var': V('x') + 4 + 2,
        'expected_query': 'chain: (x + $1) + $2',
        'expected_params': [4, 2],
    },
    {
        'template': 'complex: {{ var }}',
        'var': (Var('foo') > 2) & ((S('x') / 7 > 3) | (Var('another') ** 4 == 42)),
        'expected_query': 'complex: (foo > $1) AND (($2 / $3) > $4) OR (another ^ $5) = $6',
        'expected_params': [2, 'x', 7, 3, 4, 42],
    },
]


@pytest.mark.parametrize(','.join(args), [[t[a] for a in args] for t in TESTS], ids=[t['template'] for t in TESTS])
def test_render(template, var, expected_query, expected_params):
    query, params = render(template, var=var)
    assert query == expected_query
    assert params == expected_params


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
])
def test_simple_blocks(block, expected_query):
    query, _ = render('{{ v }}', v=block)
    assert query == expected_query


@pytest.mark.parametrize('block,s', [
    (SqlBlock(1) == 2, '<SqlBlock(1 = 2)>'),
    (SqlBlock('x') != 1, '<SqlBlock(x != 1)>'),
    (SqlBlock('y') < 2, '<SqlBlock(y < 2)>'),
])
def test_block_repr(block, s):
    assert repr(block) == s
