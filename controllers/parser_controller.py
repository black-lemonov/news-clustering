from typing import final

from db_context.sqlite_context import DBContext
from dto.article import Article


@final
class ParserController:
    __db_context: DBContext

    def __init__(self, db_context: DBContext) -> None:
        self.__db_context = db_context

    def save_article(self, article: Article) -> None:
        url = article.url
        title = article.title
        content = article.description
        date = article.date
        self.__db_context.insert(
            (url, title, content, date)
        )


