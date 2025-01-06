import sqlite3

from typing import final

from controllers.articles_repository import ArticlesRepository
from db.db_context import DBContext
from dto.article import Article


@final
class DBRepository(ArticlesRepository):
    __db_context: DBContext

    def __init__(self, db_context: DBContext) -> None:
        self.__db_context = db_context

    def save_article(self, article: Article) -> None:
        title = article.title
        url = article.url
        date = article.date
        content = article.description
        self.__db_context.insert_values(
            (title, url, date, content)
        )

    def delete_old(self, days: int) -> None:
        try:
            self.__db_context.delete_where_days_limit(days)
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при удалении записей: {e}")

    def get_clusters_headers(self) -> list[Article]:
        try:
            return [
                Article(title=title, date=date, cluster_n=cluster_n)
                for title, date, cluster_n
                in self.__db_context.select_min_date_by_clusters()
            ]
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при загрузке записей: {e}")

    def get_article_by_cluster(self, cluster_n: int) -> list[Article]:
        try:
            return [
                Article(url=url, title=title, date=self.__format_date(date))
                for url, title, date
                in self.__db_context.select_by_cluster(cluster_n)
            ]
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print(f"Ошибка при загрузке записей: {e}")

    @staticmethod
    def __format_date(date_str: str) -> str:
        return '.'.join(date_str.split('-')[::-1])
