import asyncio
import os
import sqlite3

import httpx
import nltk
from apscheduler.schedulers.background import BackgroundScheduler

from dotenv import load_dotenv

from clustering.clustering_db import ClusteringDB
from logger import SimpleLogger
from parsing.parsers import K24Parser, KNParser, KTParser, LKParser
from repository import SQLiteRepository


nltk.download('stopwords')

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
LOGGER_CONFIG_PATH = os.getenv("LOGGER_CONFIG_PATH")
PARSER_INTERVAL = 300
# CLEANER_TIMEOUT = 5 * 24 * 3600

logger = SimpleLogger.create_from_config(LOGGER_CONFIG_PATH)

# cleaner_timer: Thread = Thread(
#     target=time.sleep,
#     args=(CLEANER_TIMEOUT,),
#     daemon=True
# )

repository = SQLiteRepository(db_path=DB_PATH, logger=logger)

def try_create_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "Articles" (
                    "url"	TEXT,
                    "title"	TEXT,
                    "description"	TEXT,
                    "date"	TEXT,
                    "cluster_n"	INTEGER,
                    PRIMARY KEY("url")
                )
                """
            )
            conn.commit()
    except (sqlite3.OperationalError, sqlite3.Error) as e:
        logger.error(f"Ошибка при удалении записей: {e}")

def schedule_parsers():
    async def run_parsers():
        async with httpx.AsyncClient() as http_client:
            k24 = K24Parser(
                repositories=[repository],
                logger=logger,
                http_client=http_client,
                parse_interval_sec=PARSER_INTERVAL
            )
            kn = KNParser(
                repositories=[repository],
                logger=logger,
                http_client=http_client,
                parse_interval_sec=PARSER_INTERVAL
            )
            kt = KTParser(
                repositories=[repository],
                logger=logger,
                http_client=http_client,
                parse_interval_sec=PARSER_INTERVAL
            )
            lk = LKParser(
                repositories=[repository],
                logger=logger,
                http_client=http_client,
                parse_interval_sec=PARSER_INTERVAL
            )
            clustering_db = ClusteringDB(DB_PATH)

            await parse_all(k24, kn, kt, lk, clustering_db)

    asyncio.run(run_parsers())

async def parse_all(k24, kn, kt, lk, clustering_db):
    await asyncio.gather(
        k24.parse(),
        kn.parse(),
        kt.parse(),
        lk.parse()
    )
    clustering_db.run()

scheduler = BackgroundScheduler()
scheduler.add_job(schedule_parsers, 'interval', seconds=PARSER_INTERVAL)

def start_parsers():
    logger.info("Запуск парсеров...")
    scheduler.start()

def stop_parsers():
    scheduler.shutdown()
    logger.info("Парсеры остановлены")

if __name__ == '__main__':
    # clustering_db = ClusteringDB(DB_PATH)
    # clustering_db.run()
    schedule_parsers()
