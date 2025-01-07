import pytest

from db_context.sqlite_context import SQLiteDBContext


@pytest.fixture(scope="session")
def db_context():
    db_context = SQLiteDBContext(":memory:")
    yield db_context
    db_context.close()