import asyncio

import httpx
import pytest

from controllers.parser_controller import ParserController
from db_context.sqlite_context import SQLiteDBContext
from parsers.k24_parser import K24Parser
from parsers.kn_parser import KNParser
from parsers.kt_parser import KTParser
from parsers.lk_parser import LKParser

PARSE_INTERVAL = 10

@pytest.mark.asyncio
async def test_parsers():
    db_context = SQLiteDBContext("../resources/articles.db")
    parser_controller = ParserController(db_context)
    async with httpx.AsyncClient() as http_client:
        k24 = K24Parser(
            parser_controller=parser_controller,
            http_client=http_client,
            parse_interval_sec=PARSE_INTERVAL
        )
        kn = KNParser(
            parser_controller=parser_controller,
            http_client=http_client,
            parse_interval_sec=PARSE_INTERVAL
        )
        kt = KTParser(
            parser_controller=parser_controller,
            http_client=http_client,
            parse_interval_sec=PARSE_INTERVAL
        )
        lk = LKParser(
            parser_controller=parser_controller,
            http_client=http_client,
            parse_interval_sec=PARSE_INTERVAL
        )

        await asyncio.gather(
            k24.parse(),
            kn.parse(),
            kt.parse(),
            lk.parse()
        )

if __name__ == "__main__":
    asyncio.run(test_parsers())