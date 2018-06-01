import pytest

from buildpg import MultipleValues, Select, Values, render

args = 'template', 'ctx', 'expected_query', 'expected_params'
TESTS = [
    {
        'template': 'simple: {{ v }}',
        'ctx': lambda: dict(v=1),
        'expected_query': 'simple: $1',
        'expected_params': [1],
    },
    {
        'template': 'multiple: {{ a}} {{c }} {{b}}',
        'ctx': lambda: dict(a=1, b=2, c=3),
        'expected_query': 'multiple: $1 $2 $3',
        'expected_params': [1, 3, 2],
    },
    {
        'template': 'values: {{ a }}',
        'ctx': lambda: dict(a=Values(1, 2, 3)),
        'expected_query': 'values: ($1, $2, $3)',
        'expected_params': [1, 2, 3],
    },
    {
        'template': 'named values: {{ a }} {{ a.names }}',
        'ctx': lambda: dict(a=Values(foo=1, bar=2)),
        'expected_query': 'named values: ($1, $2) foo, bar',
        'expected_params': [1, 2],
    },
    {
        'template': 'multiple values: {{ a }}',
        'ctx': lambda: dict(a=MultipleValues(
            Values(3, 2, 1),
            Values('i', 'j', 'k')
        )),
        'expected_query': 'multiple values: ($1, $2, $3), ($4, $5, $6)',
        'expected_params': [3, 2, 1, 'i', 'j', 'k'],
    },
    {
        'template': 'raw: {{the_raw_values}}',
        'ctx': lambda: dict(the_raw_values=Select('x', 'y', '4')),
        'expected_query': 'raw: x, y, 4',
        'expected_params': [],
    },
    {
        'template': 'select as: {{ select_as }}',
        'ctx': lambda: dict(select_as=Select(foo='foo_named', bar='bar_named', cat='dog')),
        'expected_query': 'select as: foo_named AS foo, bar_named AS bar, dog AS cat',
        'expected_params': [],
    },
]


@pytest.mark.parametrize(','.join(args), [[t[a] for a in args] for t in TESTS], ids=[t['template'] for t in TESTS])
def test_render(template, ctx, expected_query, expected_params):
    ctx = ctx()
    query, params = render(template, **ctx)
    assert expected_query == query
    assert expected_params == params


@pytest.mark.parametrize('component,s', [
    (lambda: Select('a', 'b', 'c'), '<Select(a, b, c)>'),
    (lambda: MultipleValues(Values(3, 2, 1), Values(1, 2, 3)), '<MultipleValues((3, 2, 1), (1, 2, 3))>'),
])
def test_component_repr(component, s):
    assert s == repr(component())
