from dto.article_selectors import ArticleSelectors
from parsers.base_parser import BaseParser


class KNParser(BaseParser):
    site_url: str = "https://kubnews.ru/all/?type=news"

    _selectors = ArticleSelectors(
        article="a.card",
        title="div.card__description::text",
        url="",
        date="div.card__info span.card__date::text",
        content="div.material__content p::text"
    )

    def _parse_url(self) -> None:
        short_url = self._article.attrib['href'].strip()
        self._parsed_article.url = f"https://kubnews.ru{short_url}"