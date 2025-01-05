import asyncio
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta

import httpx
from scrapy import Selector

from logger import Logger
from repository import NewsRepository, News


class Parser(ABC):
    site_url: str

    _repositories: list[NewsRepository]
    _logger: Logger
    _http_client: httpx.AsyncClient

    _parse_interval_sec: int
    _parsed_urls_buffer_limit: int = 30
    _parsed_urls_buffer: deque[str]   # здесь будет очередь из разных новостей
    _tmp_urls_buffer: deque[str]    # здесь будут все новости с одной страницы

    _stopwords: set[str] = {"ТОП", "Топ", "топ"}

    _article: Selector
    _parsed_news: News

    _article_css: str
    _title_css: str
    _url_css: str
    _date_css: str
    _content_css: str

    def __init__(
            self,
            repositories: list[NewsRepository],
            logger: Logger,
            http_client: httpx.AsyncClient,
            parse_interval_sec: int
    ) -> None:
        self._repositories = repositories
        self._logger = logger
        self._http_client = http_client
        self._parse_interval_sec = parse_interval_sec
        self._parsed_urls_buffer = deque(maxlen=self._parsed_urls_buffer_limit)
        self._tmp_urls_buffer = deque()

    def add_storage(self, storage: NewsRepository) -> None:
        self._repositories.append(storage)

    def remove_storage(self, storage: NewsRepository) -> None:
        self._repositories.remove(storage)

    async def parse(self) -> None:
        await self._try_get_main_page()
        for article in self._get_articles():
            self._article = article
            self._create_blank_news()
            self._parse_url()
            if self._in_parsed_urls():
                continue
            self._save_to_tmp_buffer()
            self._parse_title()
            if self._is_spam():
                continue
            self._parse_date()
            await self._sleep()
            await self._parse_content()
            self._save_to_storage()
            self._save_to_urls_buffer()

    async def _try_get_main_page(self) -> None:
        self._main_page: str = ""
        self._logger.info(f"Отправляю запрос к {self.site_url}...")
        try:
            response = (
                await self._http_client.get(self.site_url)
            ).raise_for_status()
            self._main_page: str = response.text
        except httpx.HTTPError as e:
            self._logger.error(f"Ошибка при парсинге {self.site_url}: {repr(e)}")

    def _get_articles(self):
        selector = Selector(text=self._main_page)
        return selector.css(self._article_css)

    def _create_blank_news(self) -> None:
        self._parsed_news = News()

    def _parse_url(self) -> None:
        url = self._article.css(self._url_css).get().strip()
        self._parsed_news.url = url

    def _in_parsed_urls(self) -> bool:
        url = self._parsed_news.url
        return url in self._parsed_urls_buffer

    def _save_to_tmp_buffer(self) -> None:
        url = self._parsed_news.url
        self._tmp_urls_buffer.appendleft(url)

    def _parse_title(self) -> None:
        title = self._article.css(self._title_css).get().strip()
        self._parsed_news.title = title

    def _is_spam(self) -> bool:
        title = self._parsed_news.title
        return title in self._stopwords

    def _parse_date(self) -> None:
        date = self._article.css(self._date_css).get().strip()
        self._parsed_news.date = self._format_date(date)

    @staticmethod
    @abstractmethod
    def _format_date(date: str) -> str:
        ...

    async def _parse_content(self) -> None:
        await self.__try_get_article()

    async def __try_get_article(self) -> None:
        article = await self._http_client.get(self._parsed_news.url)
        try:
            article.raise_for_status()
            selector = Selector(text=article.text)
            content = ' '.join(
                [
                    p.strip() for p in selector.css(self._content_css).getall()
                ]
            )
            self._parsed_news.content = content
        except httpx.HTTPError as e:
            self._logger.error(f"Ошибка при парсинге {self.site_url}: {repr(e)}")

    def _save_to_storage(self) -> None:
        for storage in self._repositories:
            storage.save_news(self._parsed_news)
            self._logger.info(f"Сохранено в {repr(storage)}")

    def _save_to_urls_buffer(self) -> None:
        self._parsed_urls_buffer.extend(self._tmp_urls_buffer)
        self._tmp_urls_buffer.clear()

    async def _sleep(self) -> None:
        self._logger.info(f"Жду {self._parse_interval_sec} сек...")
        await asyncio.sleep(self._parse_interval_sec)


class K24Parser(Parser):
    site_url: str = "https://kuban24.tv/news"

    _article_css: str = "div.news-card"
    _title_css: str = "a.news-card-title::text"
    _url_css: str = "a.news-card-title::attr(href)"
    _date_css: str = "div.news-card-head div.news-card-date::text"
    _content_css: str = "div[itemprop=\"description\"] > p::text"

    @staticmethod
    def _format_date(date: str) -> str:
        return '-'.join(date.split(' ')[0].split('.')[::-1])


class KNParser(Parser):
    site_url: str = "https://kubnews.ru/all/?type=news"

    _article_css: str = "a.card"
    _title_css: str = "div.card__description::text"
    _date_css: str = "div.card__info span.card__date::text"
    _content_css: str = "div.material__content p::text"

    def _parse_url(self) -> None:
        short_url = self._article.attrib['href'].strip()
        self._parsed_news.url = f"https://kubnews.ru{short_url}"

    @staticmethod
    def _format_date(date: str) -> str:
        if "минут" in date:
            date = datetime.today().isoformat()
        elif "сегодня" in date:
            date = datetime.today().isoformat()
        elif "вчера" in date:
            date = (datetime.today() - timedelta(days=1)).isoformat()
        else:
            date = '-'.join(date.split(' ')[0].split('.')[::-1])
        return date


class KTParser(Parser):
    site_url: str = "https://kubantoday.ru/allposts/"

    _article_css: str = "a.card"
    _title_css: str = "article"
    _url_css: str = "h3 a::attr(href)"
    _date_css: str = "div.feed-news-full__card-datetime div.feed-news-full__card-time::text"
    _content_css: str = "article > p::text"

    @staticmethod
    def _format_date(date: str) -> str:
        if "Сегодня" in date:
            date = datetime.today().isoformat()
        elif "Вчера" in date:
            date = (datetime.today() - timedelta(days=1)).isoformat()
        else:
            date = '-'.join(date.split(' ')[1].split('.')[::-1])
        return date


class LKParser(Parser):
    site_url: str = "https://www.livekuban.ru/news"

    _article_css: str = "div.node--news"
    _title_css: str = "div.node--description span::text"
    _url_css: str = "div.node--description a::attr(href)"
    _date_css: str = "div.date::text"
    _content_css: str = "div.article-content > p::text"

    @staticmethod
    def _format_date(date: str) -> str:
        return '-'.join(date.split(' ')[0].split('.')[::-1])
