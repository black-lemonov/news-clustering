"""
Парсеры кубанских новостных сайтов

Содержит асинхронные методы для парсинга таких сайтов, как: kuban24.tv, kubnews.ru, kubantoday.ru и livekuban.ru.
Методы возвращают результат парсинга в виде словаря, содержащего ссылку на статью, её заголовок и полный текст.

Главная функция для запуска всех парсеров - parse_all. Записывает данные в базу данных sqlite.  
"""

from datetime import datetime, timedelta
from scrapy.selector import Selector
from typing import Callable
from logging import Logger, getLogger
from operator import itemgetter
import logging.config
import sqlite3
import asyncio
import httpx
import json


async def k24_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> list[tuple[str, ...]]:
    """
    Парсер для kuban24.tv
    """
    site_url = "https://kuban24.tv/news"
    
    results: list[tuple[str, ...]] = []
    
    try:
        response = await httpx_client.get(site_url)
    
        selector = Selector(text=response.raise_for_status().text)

        for article in selector.css('div.news-card'):
            title = article.css('a.news-card-title::text').get().strip()
            url = article.css('a.news-card-title::attr(href)').get().strip()
            
            date = article.css("div.news-card-head div.news-card-date::text").get().strip()
            date = date.split(' ')[0].split('.')
            date.reverse()
            date = '-'.join(date)
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div[itemprop="description"] > p::text').getall()])    
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(10)
        
        if log: log.info("Запарсено %d новостей с %s", len(results), site_url) 
    
    except httpx.NetworkError | httpx.InvalidURL | httpx.ConnectTimeout | httpx.HTTPStatusError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
    
    except httpx.HTTPError | httpx.ConnectError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        
    
        
        
async def kn_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> list[tuple[str, ...]]:
    """
    Парсер kubnews.ru
    """
    site_url = "https://kubnews.ru/all/?type=news" 
    
    results: list[tuple[str, ...]] = []
    
    try:
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)    
        
        for article in selector.css('a.card'):
            title = article.css('div.card__description::text').get().strip()
            url = "https://kubnews.ru" + article.attrib['href'].strip()
            
            date = article.css("div.card__info span.card__date::text").get().strip()
            
            if "минут" in date:
                date = datetime.datetime.today().isoformat()
            elif "сегодня" in date:
                print("DEBUG")
                date = datetime.datetime.today().isoformat()
            elif "вчера" in date:
                date = (datetime.datetime.today() - timedelta(days=1)).isoformat()
            else:
                date = date.split(' ')[0].split('.')
                date.reverse()
                date = '-'.join(date)
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.material__content p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(10)
        
        if log: log.info("Запарсено %d новостей с %s", len(results), site_url) 
    
    except httpx.NetworkError | httpx.InvalidURL | httpx.ConnectTimeout | httpx.HTTPStatusError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
    
    except httpx.HTTPError | httpx.ConnectError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
            

async def kt_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> list[tuple[str, ...]]:
    """
    Парсер для kubantoday.ru
    """
    site_url = "https://kubantoday.ru/allposts/"              
    
    results: list[tuple[str, ...]] = []
    
    try:
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)  
        
        for article in selector.css('article'):
            title = article.css('h3 a::text').get().strip()
            url = article.css('h3 a::attr(href)').get().strip()
            
            date = article.css("div.feed-news-full__card-datetime div.feed-news-full__card-time::text").get().strip()
            
            if "Сегодня" in date:
                date = datetime.datetime.today().isoformat()
            elif "Вчера" in date:
                date = (datetime.datetime.today() - timedelta(days=1)).isoformat()
            else:
                date = date.split(' ')[1].split('.')
                date.reverse()
                date = '-'.join(date)
                            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('article > p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(10)
        
        if log: log.info("Запарсено %d новостей с %s", len(results), site_url) 
    
    except httpx.NetworkError | httpx.InvalidURL | httpx.ConnectTimeout | httpx.HTTPStatusError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
    
    except httpx.HTTPError | httpx.ConnectError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        

async def lk_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> list[tuple[str, ...]]:
    """
    Парсер livekuban.ru
    """
    site_url = "https://www.livekuban.ru/news"
    
    results = {}
    
    try: 
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)
        
        for article in selector.css("div.node--news"):
            title = article.css('div.node--description span::text').get().strip()
            url = article.css('div.node--description a::attr(href)').get().strip()
            
            date = article.css("div.date::text").get().strip()
            date = date.split(' ')[0].split('.')
            date.reverse()
            date = '-'.join(date)
        
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.article-content > p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(10)
        
        if log: log.info("Запарсено %d новостей с %s", len(results), site_url) 
    
    except httpx.NetworkError | httpx.InvalidURL | httpx.ConnectTimeout | httpx.HTTPStatusError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
    
    except httpx.HTTPError | httpx.ConnectError as e:
        if log: log.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        

async def parse_many(
    *parsers: Callable[[httpx.AsyncClient, Logger | None], dict[str, tuple[str, ...]]],
    db_path: str,
    log: Logger = None) -> None:
    """
    Запускает переданные парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            parsed_urls: list[str] = []
            
            
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("select url from Articles")
                parsed_urls = list(
                    map(itemgetter(0), db_cursor.fetchall())
                )

            if log: log.debug("запуск парсеров")
            
            inter_res = await asyncio.gather(
                *map(lambda f: f(httpx_client, log), parsers)
            )
            
            total_posts: int = sum(map(len, inter_res))
            if log: log.info("запарсено всего %d новостей", total_posts) 
            
            stopwords: set[str] = set(["ТОП"])
            
            new_posts: int = 0
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                for site in inter_res:
                    for url, title, descr, date in site:
                        if any(w in title for w in stopwords):
                            continue
                        if any(col == "" for col in site):
                            continue
                        if url not in parsed_urls:
                            db_cursor.execute(
                                "insert into Articles values(?, ?, ?, ?, -1)",
                                (url, title, descr, date)
                            )
                            parsed_urls.append(url) 
                            new_posts += 1
            
            if log: log.info("в бд добавлено %d новостей", new_posts)
    
    except sqlite3.OperationalError as e:
        if log: log.error("ошибка при добавлении записей: %s", e)


async def parse_all(
    db_path: str,
    log: Logger = None) -> None:
    """
    Запускает все парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            
            parsed_urls: list[str] = []
            
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("select url from Articles")
                parsed_urls = list(
                    map(itemgetter(0), db_cursor.fetchall())
                )

            if log: log.debug("запуск парсеров")
            
            inter_res = await asyncio.gather(
                k24_parser(httpx_client, log),
                kn_parser(httpx_client, log),
                kt_parser(httpx_client, log),
                lk_parser(httpx_client, log)
            )
            
            total_posts: int = sum(map(len, inter_res))
            if log: log.info("запарсено всего %d новостей", total_posts) 
            
            stopwords: set[str] = set(["ТОП"])
            
            new_posts: int = 0
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                for site in inter_res:
                    for url, title, descr, date in site:
                        if any(w in title for w in stopwords):
                            continue
                        if any(col == "" for col in site):
                            continue
                        if url not in parsed_urls:
                            db_cursor.execute(
                                "insert into Articles values(?, ?, ?, ?, -1)",
                                (url, title, descr, date)
                            )
                            parsed_urls.append(url) 
                            new_posts += 1
            
            if log: log.info("в бд добавлено %d новостей", new_posts)
    
    except sqlite3.OperationalError as e:
        if log: log.error("ошибка при добавлении записей: %s", e)
    
        
if __name__ == "__main__":
    
    logger = None
    try:
        with open("logging.conf") as file:
            config = json.load(file)
        
        logging.config.dictConfig(config)
        logger = getLogger()

    except FileNotFoundError:
        print("ошибка при загрузке конфигурации логгера")
        
    asyncio.run(parse_all(db_path="articles2.db", log=logger))