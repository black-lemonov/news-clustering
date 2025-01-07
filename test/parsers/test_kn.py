import pytest

from parsers.kn_parser import KNParser

PARSER_INTERVAL_SEC = 10

@pytest.fixture
def kn(httpx_client, parser_controller):
    yield KNParser(parser_controller, httpx_client, PARSER_INTERVAL_SEC)

@pytest.mark.asyncio
async def test_parse(kn, db_context):
    rows_before = db_context.count_rows()
    await kn.parse()
    rows_after = db_context.count_rows()
    assert rows_before < rows_after


