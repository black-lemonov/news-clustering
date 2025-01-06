from dto.article_selectors import ArticleSelectors
from parsers.base_parser import BaseParser


class LKParser(BaseParser):
    site_url: str = "https://www.livekuban.ru/news"

    _selectors = ArticleSelectors(
        article="div.node--news",
        title="div.node--description span::text",
        url="div.node--description a::attr(href)",
        date="div.date::text",
        content="div.article-content > p::text"
    )
