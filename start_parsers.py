import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import httpx

from clustering.dbscan import DBSCANAlgorithm
from controllers.cleaner_controller import CleanerController
from controllers.clustering_controller import ClusteringController
from controllers.parser_controller import ParserController
from parsers.k24_parser import K24Parser
from parsers.kn_parser import KNParser
from parsers.kt_parser import KTParser
from parsers.lk_parser import LKParser
from start_db import db_context
from vectorization.stemmed_vectorizer import StemmedVectorizer

PARSE_INTERVAL = 10
SCHEDULER_INTERVAL = 3600

scheduler = BackgroundScheduler()
parser_controller = ParserController(db_context)
cleaner_controller = CleanerController(db_context)
clustering_controller = ClusteringController(db_context, StemmedVectorizer(), DBSCANAlgorithm())

async def parse_all(k24, kn, kt, lk):
    await asyncio.gather(
        k24.parse(),
        kn.parse(),
        kt.parse(),
        lk.parse()
    )
    cleaner_controller.clean_old()
    clustering_controller.add_clusters()

def schedule_parsers():
    async def run_parsers():
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

            await parse_all(k24, kn, kt, lk)

    asyncio.run(run_parsers())

scheduler.add_job(schedule_parsers, 'interval', seconds=SCHEDULER_INTERVAL)

def start_parsers():
    scheduler.start()

def stop_parsers():
    scheduler.shutdown()


