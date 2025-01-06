from dto.article_selectors import ArticleSelectors
from parsers.base_parser import BaseParser


class K24Parser(BaseParser):
    site_url: str = "https://kuban24.tv/news"

    _selectors = ArticleSelectors(
        article="div.news-card",
        title="a.news-card-title::text",
        url="a.news-card-title::attr(href)",
        date="div.news-card-head div.news-card-date::text",
        content="div[itemprop=\"description\"] > p::text"
    )

