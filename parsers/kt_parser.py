from dto.article_selectors import ArticleSelectors
from parsers.base_parser import BaseParser


class KTParser(BaseParser):
    site_url: str = "https://kubantoday.ru/allposts/"

    _selectors = ArticleSelectors(
        article="a.card",
        title="article",
        url="h3 a::attr(href)",
        date="div.feed-news-full__card-time div.feed-news-full__card-time::text",
        content="article > p::text"
    )
