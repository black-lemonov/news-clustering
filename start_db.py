import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv

from db_context.sqlite_context import SQLiteDBContext

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def adapt_datetime_iso(val):
    return val.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime_iso)

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_converter("datetime", convert_datetime)

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

try_create_db()
db_context = SQLiteDBContext(DB_PATH)
