import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from operator import itemgetter

from typing import final


@dataclass
class News:
    title: str = ""
    url: str = ""
    date: str = ""
    content: str = ""


class NewsRepository(ABC):
    @abstractmethod
    def save_news(self, news: News) -> None:
        ...


@final
class FileRepository(NewsRepository):
    path: str = "./resources/news.txt"

    def save_news(self, news: News) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(str(news))
            f.write("\n")

@final
class SQLiteRepository(NewsRepository):
    db_path: str = "./resources/articles.db"   # лучше news.db
    _con: sqlite3.Connection
    _parsed_urls: list[str]
    _stopwords: set[str] = {"ТОП"}

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
        if any(w in title for w in self._stopwords):
            return
        if url not in self._parsed_urls:
            cursor = self._con.cursor()
            cursor.execute(
                "INSERT INTO Articles VALUES(?, ?, ?, ?, -1)",
                (url, title, content, date)
            )
            self._parsed_urls.append(url)