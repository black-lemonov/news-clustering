import asyncio
import datetime
from collections import deque
from typing import final

import dateparser
import httpx
from flask import current_app
from scrapy import Selector

from flaskr.resources.db import get_db


@final
class NewsParser:
    def __init__(
            self,
            site_url: str,
            article_selector: str,
            title_selector: str,
            url_selector: str,
            date_selector: str,
            content_selector: str,
            stop_words: list[str],
            parse_interval_sec: float,
            articles_buffer_size: int
    ) -> None:
        self.__site_url: str = site_url
        self.__article_selector: str = article_selector
        self.__title_selector: str = title_selector
        self.__url_selector: str = url_selector
        self.__date_selector: str = date_selector
        self.__content_selector: str = content_selector
        self.__stop_words: set[str] = set(stop_words)
        self.__parse_interval_sec: float = parse_interval_sec
        self.__articles_buffer: deque[str] = deque(maxlen=articles_buffer_size)   # здесь будет очередь из разных новостей
        self.__tmp_buffer: deque[str] = deque(maxlen=articles_buffer_size)  # здесь будут все новости с одной страницы

    async def parse(self) -> None:
        current_app.logger.info("Отправляю запрос к %s ...", self.__site_url)
        async with httpx.AsyncClient() as client:
            articles = await self.__try_get_articles_from_main_page(client)
            if articles is None:
                current_app.logger.info(f"Ничего не запарсено: {self.__site_url} .")
                return

            for a in articles:
                article_dict = {}
                url = self.__get_url(a)
                if self.__has_been_parsed(url):
                    continue
                article_dict["url"] = url

                title = self.__get_title(a)
                if self.__is_spam(title):
                    # Это спам
                    continue
                article_dict["title"] = title

                self.__save_to_tmp_buffer(url)

                date = self.__get_date(a)
                article_dict["date"] = date

                await self.__wait_parse_interval()

                current_app.logger.info("Отправляю запрос к %s ...", self.__site_url)
                content = await self.__try_get_article_content(client, url)
                article_dict["content"] = content

                self.__save_to_db(article_dict)
                self.__save_to_buffer()

    async def __try_get_articles_from_main_page(self, client: httpx.AsyncClient):
        try:
            main_page: str = (
                await client.get(self.__site_url)
            ).raise_for_status().text
            return Selector(text=main_page).css(self.__article_selector)
        except httpx.HTTPError as e:
            current_app.logger.error("Ошибка при парсинге %s: %s", self.__site_url, e)

    def __get_url(self, selector) -> str:
        return selector.css(self.__url_selector).get().strip()

    def __get_title(self, selector) -> str:
        return selector.css(self.__title_selector).get().strip()

    def __get_date(self, selector) -> datetime.datetime:
        raw_date = selector.css(self.__date_selector).get().strip()
        return self.__format_date(raw_date)

    def __has_been_parsed(self, url: str) -> bool:
        return url in self.__articles_buffer

    def __clear_tmp_buffer(self):
        self.__tmp_buffer.clear()

    def __is_spam(self, title: str) -> bool:
        return title in self.__stop_words

    def __save_to_tmp_buffer(self, url: str) -> None:
        self.__tmp_buffer.appendleft(url)

    @staticmethod
    def __format_date(date: str) -> datetime.datetime:
        return dateparser.parse(date, languages=["ru"], settings={'DATE_ORDER': 'DMY'})

    async def __wait_parse_interval(self):
        await asyncio.sleep(self.__parse_interval_sec)

    async def __try_get_article_content(self, client: httpx.AsyncClient, url: str) -> str:
        try:
            article = (
                await client.get(url)
            ).raise_for_status().text
            selector = Selector(text=article)
            return self.__get_content(selector)
        except httpx.HTTPError as e:
            current_app.logger.error("Ошибка при парсинге %s: %s", self.__site_url, e)
            self.__clear_tmp_buffer()

    def __get_content(self, selector) -> str:
        return ' '.join(
            [ p.strip() for p in selector.css(self.__content_selector).getall() ]
        )

    @staticmethod
    def __save_to_db(article_dict: dict) -> None:
        db = get_db()
        try:
            db.execute(
                "INSERT INTO article (url, title, date, content) VALUES(:url, :title, :date, :content)",
                article_dict
            )
            db.commit()
        except db.IntegrityError:
            current_app.logger.error(
                "Статья %s уже была запарсена.",
                article_dict["url"]
            )
        else:
            current_app.logger.info(
                "Статья %s сохранена в базу данных!",
                article_dict["url"]
            )

    def __save_to_buffer(self) -> None:
        self.__articles_buffer.extend(self.__tmp_buffer)
        self.__clear_tmp_buffer()
