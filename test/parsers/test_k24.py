import pytest

from parsers.k24_parser import K24Parser

PARSER_INTERVAL_SEC = 10

@pytest.fixture
def k24(httpx_client, parser_controller):
    yield K24Parser(parser_controller, httpx_client, PARSER_INTERVAL_SEC)

@pytest.mark.asyncio
async def test_parse(k24, db_context):
    rows_before = db_context.count_rows()
    await k24.parse()
    rows_after = db_context.count_rows()
    assert rows_before < rows_after