from controllers.cleaner_controller import CleanerController
from db_context.sqlite_context import SQLiteDBContext


def test_cleaner():
    db_context = SQLiteDBContext("../resources/articles.db")
    cleaner = CleanerController(db_context, days_limit=10)
    cleaner.clean_old()