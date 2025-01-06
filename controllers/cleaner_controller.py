import sqlite3

from db_context.sqlite_context import DBContext


class CleanerController:
    __db_context: DBContext
    __days_limit: int

    def __init__(self, db_context: DBContext, days_limit: int):
        self.__db_context = db_context
        self.__days_limit = days_limit

    def clean_old(self) -> None:
        try:
            self.__db_context.delete_where_days_limit(self.__days_limit)
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при удалении записей: {e}")
