import pytest

from buildpg import BuildError, MultipleValues, Renderer, UnsafeError, Values, VarLiteral, render

args = 'template', 'ctx', 'expected_query', 'expected_params'
TESTS = [
    {
        'template': 'simple: :v',
        'ctx': lambda: dict(v=1),
        'expected_query': 'simple: $1',
        'expected_params': [1],
    },
    {
        'template': 'multiple: :a :c :b',
        'ctx': lambda: dict(a=1, b=2, c=3),
        'expected_query': 'multiple: $1 $2 $3',
        'expected_params': [1, 3, 2],
    },
    {
        'template': 'values: :a',
        'ctx': lambda: dict(a=Values(1, 2, 3)),
        'expected_query': 'values: ($1, $2, $3)',
        'expected_params': [1, 2, 3],
    },
    {
        'template': 'named values: :a :a__names',
        'ctx': lambda: dict(a=Values(foo=1, bar=2)),
        'expected_query': 'named values: ($1, $2) foo, bar',
        'expected_params': [1, 2],
    },
    {
        'template': 'multiple values: :a',
        'ctx': lambda: dict(a=MultipleValues(
            Values(3, 2, 1),
            Values('i', 'j', 'k')
        )),
        'expected_query': 'multiple values: ($1, $2, $3), ($4, $5, $6)',
        'expected_params': [3, 2, 1, 'i', 'j', 'k'],
    },
    {
        'template': 'numeric: :1000 :v1000',
        'ctx': lambda: {'1000': 1, 'v1000': 2},
        'expected_query': 'numeric: :1000 $1',
        'expected_params': [2],
    },
]


@pytest.mark.parametrize(','.join(args), [[t[a] for a in args] for t in TESTS], ids=[t['template'] for t in TESTS])
def test_render(template, ctx, expected_query, expected_params):
    ctx = ctx()
    query, params = render(template, **ctx)
    assert expected_query == query
    assert expected_params == params


@pytest.mark.parametrize('component,s', [
    (lambda: MultipleValues(Values(3, 2, 1), Values(1, 2, 3)), '<MultipleValues((3, 2, 1), (1, 2, 3))>'),
])
def test_component_repr(component, s):
    assert s == repr(component())


def test_different_regex():
    customer_render = Renderer('{{ ?([\w.]+) ?}}', '.')
    q, params = customer_render('testing: {{ a}} {{c }} {{b}}', a=1, b=2, c=3, x=Values(foo=1, bar=2))
    assert q == 'testing: $1 $2 $3'
    assert params == [1, 3, 2]

    q, params = customer_render('testing: {{ x }} {{ x.names }}', x=Values(foo=1, bar=2))
    assert q == 'testing: ($1, $2) foo, bar'
    assert params == [1, 2]


@pytest.mark.parametrize('query,ctx,msg', [
    (':a :b', dict(a=1), 'variable "b" not found in context'),
    (':a__names', dict(a=Values(1, 2)), '"a": "names" are not available for nameless values'),
    (':a__missing', dict(a=1), '"a": error building content, '
                               'AttributeError: \'int\' object has no attribute \'render_missing\''),
])
def test_errors(query, ctx, msg):
    with pytest.raises(BuildError) as exc_info:
        render(query, **ctx)
    assert msg in str(exc_info.value)


@pytest.mark.parametrize('func,exc', [
    (lambda: VarLiteral('"y"'), UnsafeError),
    (lambda: VarLiteral(1.1), TypeError),
    (lambda: MultipleValues(Values(1), 42), ValueError),
    (lambda: MultipleValues(Values(a=1, b=2), Values(b=1, a=2)), ValueError),
    (lambda: MultipleValues(Values(1), Values(1, 2)), ValueError),
])
def test_other_errors(func, exc):
    with pytest.raises(exc):
        func()
