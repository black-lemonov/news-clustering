import sqlite3

from db_context.sqlite_context import DBContext
from dto.article import Article


class AppController:
    __db_context: DBContext

    def __init__(self, db_context: DBContext):
        self.__db_context = db_context

    def get_clusters_headers(self) -> list[Article]:
        try:
            return self.__db_context.select_min_date_by_clusters()
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при загрузке записей: {e}")


    def get_article_by_cluster(self, cluster_n: int) -> list[Article]:
        try:
            return self.__db_context.select_by_cluster(cluster_n)
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при загрузке записей: {e}")

    @staticmethod
    def __format_date(date_str: str) -> str:
        return '.'.join(date_str.split('-')[::-1])