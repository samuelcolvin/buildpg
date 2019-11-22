import pytest

from buildpg import V, clauses, render


@pytest.mark.parametrize(
    'block,expected_query,expected_params',
    [
        (lambda: clauses.Select(['foo', 'bar']), 'SELECT foo, bar', []),
        (lambda: clauses.Select(['foo', 'bar']), 'SELECT foo, bar', []),
        (lambda: clauses.Select(V('foo').comma(V('bar'))), 'SELECT foo, bar', []),
        (lambda: clauses.Select([V('foo').as_('x'), V('bar').as_('y')]), 'SELECT foo AS x, bar AS y', []),
        (lambda: clauses.From('foobar'), 'FROM foobar', []),
        (lambda: clauses.From('foo', 'bar'), 'FROM foo, bar', []),
        (lambda: clauses.From('foo', V('bar')), 'FROM foo, bar', []),
        (lambda: clauses.Join('foobar', V('x.id') == V('y.id')), 'JOIN foobar ON x.id = y.id', []),
        (lambda: clauses.CrossJoin('xxx'), 'CROSS JOIN xxx', []),
        (lambda: clauses.From('a') + clauses.Join('b') + clauses.Join('c'), 'FROM a\nJOIN b\nJOIN c', []),
        (lambda: clauses.OrderBy('apple', V('pear').desc()), 'ORDER BY apple, pear DESC', []),
        (lambda: clauses.Limit(20), 'LIMIT $1', [20]),
        (lambda: clauses.Offset(20), 'OFFSET $1', [20]),
        (lambda: clauses.Join('foobar', V('x.value') == 0), 'JOIN foobar ON x.value = $1', [0]),
    ],
)
def test_simple_blocks(block, expected_query, expected_params):
    query, params = render(':v', v=block())
    assert expected_query == query
    assert expected_params == params


def test_where():
    query, params = render(':v', v=clauses.Where((V('x') == 4) & (V('y').like('xxx'))))
    assert 'WHERE x = $1 AND y LIKE $2' == query
    assert [4, 'xxx'] == params


@pytest.mark.parametrize('value,expected', [(0, 0), (False, False), ('', '')])
def test_falsey_values(value, expected):
    query, params = render('WHERE :a', a=V('a') == value)
    assert query == 'WHERE a = $1'
    assert params == [expected]
