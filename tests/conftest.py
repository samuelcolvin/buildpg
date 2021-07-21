import asyncio

import pytest

from buildpg import asyncpg

DB_NAME = 'buildpg_test'

# some simple data to use in queries
POPULATE_DB = """
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  company INT NOT NULL REFERENCES companies ON DELETE CASCADE,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  value INT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO companies (name, description) VALUES
  ('foobar', 'this is some test data'),
  ('egg plant', 'this is some more test data');

WITH values_ (company_name_, first_name_, last_name_, value_, created_) AS (VALUES
  ('foobar', 'Franks', 'spencer', 44, date '2020-01-28'),
  ('foobar', 'Fred', 'blogs', -10, date '2021-01-28'),
  ('egg plant', 'Joe', null, 1000, date '2022-01-28')
)
INSERT INTO users (company, first_name, last_name, value, created)
SELECT c.id, first_name_, last_name_, value_, created_ FROM values_
JOIN companies AS c ON company_name_=c.name;
"""


async def _reset_db():
    conn = await asyncpg.connect('postgresql://postgres@localhost')
    try:
        if not await conn.fetchval('SELECT 1 from pg_database WHERE datname=$1;', DB_NAME):
            await conn.execute(f'CREATE DATABASE {DB_NAME};')
    finally:
        await conn.close()
    conn = await asyncpg.connect(f'postgresql://postgres@localhost/{DB_NAME}')
    try:
        await conn.execute(POPULATE_DB)
    finally:
        await conn.close()


@pytest.fixture(scope='session')
def db():
    asyncio.run(_reset_db())


@pytest.fixture
async def conn(db):
    conn = await asyncpg.connect_b(f'postgresql://postgres@localhost/{DB_NAME}')
    tr = conn.transaction()
    await tr.start()

    yield conn

    await tr.rollback()
    await conn.close()
