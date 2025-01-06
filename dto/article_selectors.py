from dataclasses import dataclass


@dataclass
class ArticleSelectors:
    article: str
    title: str
    url: str
    date: str
    content: str