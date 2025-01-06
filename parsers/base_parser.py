import asyncio
from abc import ABC, abstractmethod
from collections import deque

import httpx
from icecream import ic
from scrapy import Selector

from controllers.parser_controller import ParserController
from dto.article import Article


class BaseSpider(ABC):
    site_url: str

    _controller: ParserController
    _http_client: httpx.AsyncClient

    _parse_interval_sec: int
    _parsed_urls_buffer_limit: int = 30
    _parsed_urls_buffer: deque[str]  # здесь будет очередь из разных новостей
    _tmp_urls_buffer: deque[str]  # здесь будут все новости с одной страницы

    _stopwords: set[str] = {"ТОП", "Топ", "топ"}

    _article: Selector
    _parsed_article: Article

    _article_css: str
    _title_css: str
    _url_css: str
    _date_css: str
    _content_css: str

    def __init__(
            self,
            parser_controller: ParserController,
            http_client: httpx.AsyncClient,
            parse_interval_sec: int
    ) -> None:
        self._controller = parser_controller
        self._http_client = http_client
        self._parse_interval_sec = parse_interval_sec
        self._parsed_urls_buffer = deque(maxlen=self._parsed_urls_buffer_limit)
        self._tmp_urls_buffer = deque()

    async def parse(self) -> None:
        ic(f"Отправляю запрос {self.site_url}")
        await self._try_get_main_page()
        for article in self._get_articles():
            ic(article)
            self._article = article
            self._create_blank_article()
            self._parse_url()
            if self._in_parsed_urls():
                continue
            self._save_to_tmp_buffer()
            self._parse_title()
            if self._is_spam():
                continue
            self._parse_date()
            await self._sleep()
            ic(f"Отправляю запрос {self._parsed_article.url}")
            await self._parse_content()
            self._save_article()
            self._save_to_urls_buffer()

    async def _try_get_main_page(self) -> None:
        self._main_page: str = ""
        try:
            response = (
                await self._http_client.get(self.site_url)
            ).raise_for_status()
            self._main_page: str = response.text
        except httpx.HTTPError as e:
            ic(f"Ошибка при парсинге {self.site_url}: {repr(e)}")

    def _get_articles(self):
        selector = Selector(text=self._main_page)
        return selector.css(self._article_css)

    def _create_blank_article(self) -> None:
        self._parsed_article = Article()

    def _parse_url(self) -> None:
        url = self._article.css(self._url_css).get().strip()
        self._parsed_article.url = url

    def _in_parsed_urls(self) -> bool:
        url = self._parsed_article.url
        return url in self._parsed_urls_buffer

    def _save_to_tmp_buffer(self) -> None:
        url = self._parsed_article.url
        self._tmp_urls_buffer.appendleft(url)

    def _parse_title(self) -> None:
        title = self._article.css(self._title_css).get().strip()
        self._parsed_article.title = title

    def _is_spam(self) -> bool:
        title = self._parsed_article.title
        return title in self._stopwords

    def _parse_date(self) -> None:
        date = self._article.css(self._date_css).get().strip()
        self._parsed_article.date = self._format_date(date)

    @staticmethod
    @abstractmethod
    def _format_date(date: str) -> str:
        ...

    async def _parse_content(self) -> None:
        await self.__try_get_article()

    async def __try_get_article(self) -> None:
        article = await self._http_client.get(self._parsed_article.url)
        try:
            article.raise_for_status()
            selector = Selector(text=article.text)
            content = ' '.join(
                [
                    p.strip() for p in selector.css(self._content_css).getall()
                ]
            )
            self._parsed_article.description = content
        except httpx.HTTPError as e:
            ic(f"Ошибка при парсинге {self.site_url}: {repr(e)}")

    def _save_article(self) -> None:
        self._controller.save_article(self._parsed_article)

    def _save_to_urls_buffer(self) -> None:
        self._parsed_urls_buffer.extend(self._tmp_urls_buffer)
        self._tmp_urls_buffer.clear()

    async def _sleep(self) -> None:
        await asyncio.sleep(self._parse_interval_sec)
