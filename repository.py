import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from operator import itemgetter

from typing import final

from lxml.xsltext import self_node

from main import logger


@dataclass
class News:
    title: str = ""
    url: str = ""
    date: str = ""
    content: str = ""
    cluster_n: int = None


class NewsRepository(ABC):
    @abstractmethod
    def save_news(self, news: News) -> None:
        ...

    @abstractmethod
    def delete_old(self, days: int) -> None:
        ...

    @abstractmethod
    def get_news_by_clusters(self, cluster_n: int) -> list[News]:
        ...

    @abstractmethod
    def get_clusters_headers(self) -> list[News]:
        ...


@final
class FileRepository(NewsRepository):
    def get_clusters_headers(self) -> list[News]:
        pass

    def get_news_by_clusters(self, cluster_n: int) -> list[News]:
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
    db_path: str = "./resources/articles.db"   # лучше news.db
    _con: sqlite3.Connection

    def __init__(self) -> None:
        self._con = sqlite3.connect(self.db_path)
        cursor = self._con.cursor()
        cursor.execute("SELECT url FROM Articles")
        self._parsed_urls = list(
            map(itemgetter(0), cursor.fetchall())
        )

    def save_news(self, news: News) -> None:
        title = news.title
        url = news.url
        date = news.date
        content = news.content
        cursor = self._con.cursor()
        cursor.execute(
            "INSERT INTO Articles VALUES(?, ?, ?, ?, -1)",
            (url, title, content, date)
        )
        self._con.commit()

    def delete_old(self, days: int) -> None:
        try:
            cursor = self._con.cursor()
            cursor.execute(
                f"DELETE FROM Articles WHERE julianday(date) - julianday(date('now')) > ?",
                (days,)
            )
            self._con.commit()

        except (sqlite3.OperationalError, sqlite3.Error) as e:
            logger.error(f"Ошибка при удалении записей: {e}")

    def get_clusters_headers(self) -> list[News]:
        try:
            cursor = self._con.cursor()
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
            logger.error(f"Ошибка при загрузке записей: {e}")

    def get_news_by_clusters(self, cluster_n: int) -> list[News]:
        try:
            cursor = self._con.cursor()
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
            logger.error(f"Ошибка при загрузке записей: {e}")

    @staticmethod
    def __format_date(date_str: str) -> str:
        return '.'.join(date_str.split('-')[::-1])
