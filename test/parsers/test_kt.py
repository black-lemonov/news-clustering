import pytest

from parsers.kt_parser import KTParser

PARSER_INTERVAL_SEC = 10

@pytest.fixture
def kt(httpx_client, parser_controller):
    yield KTParser(parser_controller, httpx_client, PARSER_INTERVAL_SEC)

@pytest.mark.asyncio
async def test_parse(kt, db_context):
    rows_before = db_context.count_rows()
    await kt.parse()
    rows_after = db_context.count_rows()
    assert rows_before < rows_after