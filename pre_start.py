import os

import nltk
from flask.cli import load_dotenv

from controllers.app_controller import AppController
from db_context.sqlite_context import SQLiteDBContext

nltk.download('stopwords')

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

db_context = SQLiteDBContext(DB_PATH)
app_controller = AppController(db_context)
