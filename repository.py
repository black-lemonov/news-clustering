import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from operator import itemgetter

from typing import final

from logger import Logger


@dataclass
class News:
    title: str = None
    url: str = None
    date: str = None
    content: str = None
    cluster_n: int = None


class NewsRepository(ABC):
    @abstractmethod
    def save_news(self, news: News) -> None:
        ...

    @abstractmethod
    def delete_old(self, days: int) -> None:
        ...

    @abstractmethod
    def get_news_by_cluster(self, cluster_n: int) -> list[News]:
        ...

    @abstractmethod
    def get_clusters_headers(self) -> list[News]:
        ...


@final
class FileRepository(NewsRepository):
    def get_clusters_headers(self) -> list[News]:
        pass

    def get_news_by_cluster(self, cluster_n: int) -> list[News]:
        pass

    path: str = "./resources/news.txt"

    def save_news(self, news: News) -> None:
        self.__write_news_to_file(news)

    def __write_news_to_file(self, news: News) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(str(news))
            f.write("\n")

    def delete_old(self, days: int) -> None:
        pass


@final
class SQLiteRepository(NewsRepository):
    _db_path: str
    _logger: Logger

    def __init__(self, db_path: str, logger: Logger) -> None:
        self._db_path = db_path
        self._logger = logger

    def save_news(self, news: News) -> None:
        title = news.title
        url = news.url
        date = news.date
        content = news.content
        with sqlite3.Connection(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Articles VALUES(?, ?, ?, ?, -1)",
                (url, title, content, date)
            )

    def delete_old(self, days: int) -> None:
        try:
            with sqlite3.Connection(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"DELETE FROM Articles WHERE julianday(date) - julianday(date('now')) > ?",
                    (days,)
                )
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            self._logger.error(f"Ошибка при удалении записей: {e}")

    def get_clusters_headers(self) -> list[News]:
        try:
            with sqlite3.Connection(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT cluster_n, title, min(date)
                    FROM Articles
                    GROUP BY cluster_n
                    """
                )
                return [
                    News(title=title, date=date, cluster_n=cluster_n)
                    for cluster_n, title, date in cursor.fetchall()
                ]
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            self._logger.error(f"Ошибка при загрузке записей: {e}")

    def get_news_by_cluster(self, cluster_n: int) -> list[News]:
        try:
            with sqlite3.Connection(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT url, title, date FROM Articles
                    WHERE cluster_n = ?
                    """,
                    (cluster_n,)
                )
                return [
                    News(url=url, title=title, date=self.__format_date(date))
                    for url, title, date in cursor.fetchall()
                ]
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            self._logger.error(f"Ошибка при загрузке записей: {e}")

    @staticmethod
    def __format_date(date_str: str) -> str:
        return '.'.join(date_str.split('-')[::-1])
