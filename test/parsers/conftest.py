import httpx
import pytest

from controllers.parser_controller import ParserController


@pytest.fixture(scope='module')
def httpx_client():
    client = httpx.AsyncClient()
    yield client

@pytest.fixture(scope='module')
def parser_controller(db_context):
    yield ParserController(db_context)
