buildpg
=======

|BuildStatus| |Coverage| |pypi|

Query building for the postgresql prepared statements and asyncpg.

Lots of more powerful features, including full clause construction, multiple values, logic functions,
query pretty-printing and different variable substitution - below is just a very quick summary.
Please check the code and tests for examples.

Building Queries
................

Simple variable substitution:

.. code-block:: python

   from buildpg import render

   render('select * from mytable where x=:foo and y=:bar', foo=123, bar='whatever')
   >> 'select * from mytable where x=$1 and y=$2', [123, 'whatever']


Use of ``V`` to substitute constants:

.. code-block:: python

   from buildpg import V, render

   render('select * from mytable where :col=:foo', col=V('x'), foo=456)
   >> 'select * from mytable where x=$1', [456]


Complex logic:

.. code-block:: python

   from buildpg import V, funcs, render

   where_logic = V('foo.bar') == 123
   if spam_value:
       where_logic &= V('foo.spam') <= spam_value

   if exclude_cake:
       where_logic &= funcs.not_(V('foo.cake').in_([1, 2, 3]))

   render('select * from foo :where', where=where_logic)
   >> 'select * from foo foo.bar = $1 AND foo.spam <= $2 AND not(foo.cake in $3)', [123, 123, ['x', 'y']]


Values usage:

.. code-block:: python

   from buildpg import Values, render

   render('insert into the_table (:values__names) values :values', values=Values(a=123, b=456, c='hello'))
   >> 'insert into the_table (a, b, c) values ($1, $2, $3)', [123, 456, 'hello']


With asyncpg
............


As a wrapper around *asyncpg*:

.. code-block:: python

   import asyncio
   from buildpg import asyncpg

   async def main():
       async with asyncpg.create_pool_b('postgres://postgres@localhost:5432/db') as pool:
           await pool.fetchval_b('select spam from mytable where x=:foo and y=:bar', foo=123, bar='whatever')
           >> 42

   asyncio.get_event_loop().run_until_complete(main())


Both the pool and connections have ``*_b`` variants of all common query methods:

- ``execute_b``
- ``executemany_b``
- ``fetch_b``
- ``fetchval_b``
- ``fetchrow_b``
- ``cursor_b``

.. |BuildStatus| image:: https://travis-ci.com/samuelcolvin/buildpg.svg?branch=master
   :target: https://travis-ci.com/samuelcolvin/buildpg
.. |Coverage| image:: https://codecov.io/gh/samuelcolvin/buildpg/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/samuelcolvin/buildpg/
.. |pypi| image:: https://img.shields.io/pypi/v/buildpg.svg
   :target: https://pypi.org/project/buildpg/
