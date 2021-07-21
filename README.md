# buildpg

[![CI](https://github.com/samuelcolvin/buildpg/workflows/ci/badge.svg?event=push)](https://github.com/samuelcolvin/buildpg/actions?query=event%3Apush+branch%3Amaster+workflow%3Aci)
[![Coverage](https://codecov.io/gh/samuelcolvin/buildpg/branch/master/graph/badge.svg)](https://codecov.io/gh/samuelcolvin/buildpg)
[![pypi](https://img.shields.io/pypi/v/buildpg.svg)](https://pypi.python.org/pypi/buildpg)
[![versions](https://img.shields.io/pypi/pyversions/buildpg.svg)](https://github.com/samuelcolvin/buildpg)
[![license](https://img.shields.io/github/license/samuelcolvin/buildpg.svg)](https://github.com/samuelcolvin/buildpg/blob/master/LICENSE)

Query building for the postgresql prepared statements and asyncpg.

Lots of more powerful features, including full clause construction, multiple values, logic functions,
query pretty-printing and different variable substitution - below is just a very quick summary.
Please check the code and tests for examples.

## Building Queries

Simple variable substitution:

```py
from buildpg import render

render('select * from mytable where x=:foo and y=:bar', foo=123, bar='whatever')
>> 'select * from mytable where x=$1 and y=$2', [123, 'whatever']
```


Use of `V` to substitute constants:

```py
from buildpg import V, render

render('select * from mytable where :col=:foo', col=V('x'), foo=456)
>> 'select * from mytable where x=$1', [456]
```

Complex logic:

```py
from buildpg import V, funcs, render

where_logic = V('foo.bar') == 123
if spam_value:
   where_logic &= V('foo.spam') <= spam_value

if exclude_cake:
   where_logic &= funcs.not_(V('foo.cake').in_([1, 2, 3]))

render('select * from foo :where', where=where_logic)
>> 'select * from foo foo.bar = $1 AND foo.spam <= $2 AND not(foo.cake in $3)', [123, 123, ['x', 'y']]
```

Values usage:

```py
from buildpg import Values, render

render('insert into the_table (:values__names) values :values', values=Values(a=123, b=456, c='hello'))
>> 'insert into the_table (a, b, c) values ($1, $2, $3)', [123, 456, 'hello']
```

## With asyncpg

As a wrapper around *asyncpg*:

```py
import asyncio
from buildpg import asyncpg

async def main():
   async with asyncpg.create_pool_b('postgres://postgres@localhost:5432/db') as pool:
       await pool.fetchval_b('select spam from mytable where x=:foo and y=:bar', foo=123, bar='whatever')
       >> 42

asyncio.run(main())
```


Both the pool and connections have `*_b` variants of all common query methods:

- `execute_b`
- `executemany_b`
- `fetch_b`
- `fetchval_b`
- `fetchrow_b`
- `cursor_b`


## Operators

| Python operator/function | SQL operator |
| ------------------------ | ------------ |
| `&`                      | `AND` |
| `|`                      | `OR` |
| `=`                      | `=` |
| `!=`                     | `!=` |
| `<`                      | `<` |
| `<=`                     | `<=` |
| `>`                      | `>` |
| `>=`                     | `>=` |
| `+`                      | `+` |
| `-`                      | `-` |
| `*`                      | `*` |
| `/`                      | `/` |
| `%`                      | `%` |
| `**`                     | `^` |
| `-`                      | `-` |
| `~`                      | `not(...)` |
| `sqrt`                   | `|/` |
| `abs`                    | `@` |
| `contains`               | `@>` |
| `contained_by`           | `<@` |
| `overlap`                | `&&` |
| `like`                   | `LIKE` |
| `ilike`                  | `ILIKE` |
| `cat`                    | `||` |
| `in_`                    | `in` |
| `from_`                  | `from` |
| `at_time_zone`           | `AT TIME ZONE` |
| `matches`                | `@@` |
| `is_`                    | `is` |
| `is_not`                 | `is not` |
| `for_`                   | `for` |
| `factorial`              | `!` |
| `cast`                   | `::` |
| `asc`                    | `ASC` |
| `desc`                   | `DESC` |
| `comma`                  | `,` |
| `on`                     | `ON` |
| `as_`                    | `AS` |
| `nulls_first`            | `NULLS FIRST` |
| `nulls_last`             | `NULLS LAST` |

Usage:

```py
from buildpg import V, S, render

def show(component):
   sql, params = render(':c', c=component)
   print(f'sql="{sql}" params={params}')

show(V('foobar').contains([1, 2, 3]))
#> sql="foobar @> $1" params=[[1, 2, 3]]
show(V('foobar') == 4)
#> sql="foobar = $1" params=[4]
show(~V('foobar'))
#> sql="not(foobar)" params=[]
show(S(625).sqrt())
#> sql="|/ $1" params=[625]
show(V('foo').is_not('true'))
#> sql="foo is not true" params=[]
```

## Functions

| Python function                             | SQL function  |
| ------------------------------------------- | ------------- |
| `AND(*args)`                                | `<arg1> and <arg2> ...` |
| `OR(*args)`                                 | `<arg1> or <arg2> ...` |
| `NOT(arg)`                                  | `not(<arg>)` |
| `comma_sep(*args)`                          | `<arg1>, <arg2>, ...` |
| `count(expr)`                               | `count(expr)` |
| `any(arg)`                                  | `any(<arg1>)` |
| `now()`                                     | `now()` |
| `cast(v, cast_type)`                        | `<v>::<cast_type>` |
| `upper(string)`                             | `upper(<string>)` |
| `lower(string)`                             | `lower(<string>)` |
| `length(string)`                            | `length(<string>)` |
| `left(string, n)`                           | `left(<string>, <n>)` |
| `right(string, n)`                          | `right(<string>, <n>)` |
| `extract(expr)`                             | `extract(<expr>)` |
| `sqrt(n)`                                   | `|/<n>` |
| `abs(n)`                                    | `@<n>` |
| `factorial(n)`                              | `!<n>` |
| `position(substring, string)`               | `position(<substring> in <st`... |
| `substring(string, pattern, escape-None)`   | `substring(<string> from <pa`... |
| `to_tsvector(arg1, document-None)`          | `to_tsvector(<arg1>)` |
| `to_tsquery(arg1, text-None)`               | `to_tsquery(<arg1>)` |

Usage:

```py
from buildpg import V, render, funcs

def show(component):
  sql, params = render(':c', c=component)
  print(f'sql="{sql}" params={params}')

show(funcs.AND(V('x') == 4, V('y') > 6))
#> sql="x = $1 AND y > $2" params=[4, 6]
show(funcs.position('foo', 'this has foo in it'))
#> sql="position($1 in $2)" params=['foo', 'this has foo in it']
```
