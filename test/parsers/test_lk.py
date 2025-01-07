import pytest

from parsers.lk_parser import LKParser

PARSER_INTERVAL_SEC = 10

@pytest.fixture
def lk(httpx_client, parser_controller):
    yield LKParser(parser_controller, httpx_client, PARSER_INTERVAL_SEC)

@pytest.mark.asyncio
async def test_parse(lk, db_context):
    rows_before = db_context.count_rows()
    await lk.parse()
    rows_after = db_context.count_rows()
    assert rows_before < rows_after