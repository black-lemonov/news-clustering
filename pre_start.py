import asyncio
import os
import sqlite3

import httpx
import nltk
from apscheduler.schedulers.background import BackgroundScheduler

from dotenv import load_dotenv

from clustering.dbscan import DBSCANAlgorithm
from controllers.app_controller import AppController
from controllers.clustering_controller import ClusteringController
from controllers.parser_controller import ParserController
from db_context.sqlite_context import SQLiteDBContext
from parsing.k24_spider import K24Spider
from parsing.kn_spider import KNSpider
from parsing.kt_spider import KTSpider
from parsing.lk_spider import LKSpider
from vectorization.stemmed_vectorizer import StemmedVectorizer

nltk.download('stopwords')

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
LOGGER_CONFIG_PATH = os.getenv("LOGGER_CONFIG_PATH")


db_context = SQLiteDBContext(DB_PATH)
parser_controller = ParserController(db_context)
app_controller = AppController(db_context)

PARSE_INTERVAL = 10
PARSING_SCHEDULER_INTERVAL = 3600
scheduler = BackgroundScheduler()


def try_create_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Articles" (
                "url"	TEXT,
                "title"	TEXT,
                "description"	TEXT,
                "date"	TEXT,
                "cluster_n"	INTEGER DEFAULT -1,
                PRIMARY KEY("url")
            )
            """
        )

def schedule_parsers():
    async def run_parsers():
        async with httpx.AsyncClient() as http_client:
            k24 = K24Spider(
                parser_controller=parser_controller,
                http_client=http_client,
                parse_interval_sec=PARSE_INTERVAL
            )
            kn = KNSpider(
                parser_controller=parser_controller,
                http_client=http_client,
                parse_interval_sec=PARSE_INTERVAL
            )
            kt = KTSpider(
                parser_controller=parser_controller,
                http_client=http_client,
                parse_interval_sec=PARSE_INTERVAL
            )
            lk = LKSpider(
                parser_controller=parser_controller,
                http_client=http_client,
                parse_interval_sec=PARSE_INTERVAL
            )
            text_vectorizer = StemmedVectorizer()
            clustering_algorithm = DBSCANAlgorithm()
            clustering_controller = ClusteringController(db_context, text_vectorizer, clustering_algorithm)

            await parse_all(k24, kn, kt, lk, clustering_controller)

    asyncio.run(run_parsers())


async def parse_all(k24, kn, kt, lk, clustering_controller):
    await asyncio.gather(
        k24.parse(),
        kn.parse(),
        kt.parse(),
        lk.parse()
    )
    clustering_controller.add_clusters()

def start_parsers():
    scheduler.add_job(schedule_parsers, 'interval', seconds=PARSING_SCHEDULER_INTERVAL)
    scheduler.start()

def stop_parsers():
    scheduler.shutdown()

if __name__ == "__main__":
    start_parsers()
