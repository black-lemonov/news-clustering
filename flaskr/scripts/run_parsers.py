import asyncio

import httpx
from flask import current_app

from flaskr.resources.parsers import get_parsers


def run_parsers():
    try:
        async def run_async_parsers():
            await asyncio.gather(*[p.parse() for p in get_parsers()])
        asyncio.run(run_async_parsers())
    except httpx.HTTPError as e:
        current_app.logger.error(e)