"""
Парсеры новостных сайтов

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


async def k24_parser(
    httpx_client: httpx.AsyncClient,
    logger: Logger,
    interval: int) -> list[tuple[str, ...]]:
    """
    Парсер для kuban24.tv
    """
    site_url = "https://kuban24.tv/news"
    
    results: list[tuple[str, ...]] = []
    
    try:
        logger.debug("отправляю запрос к %s", site_url)
        response = await httpx_client.get(site_url)
    
        selector = Selector(text=response.raise_for_status().text)

        for article in selector.css('div.news-card'):
            title = article.css('a.news-card-title::text').get().strip()
            url = article.css('a.news-card-title::attr(href)').get().strip()
            
            date = article.css("div.news-card-head div.news-card-date::text").get().strip()
            date = '-'.join(date.split(' ')[0].split('.')[::-1])
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div[itemprop="description"] > p::text').getall()])    
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(interval)
        
        logger.info("Запарсено %d новостей с %s", len(results), site_url) 
    
    except (httpx.HTTPError, httpx.InvalidURL) as e:
        logger.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        
        
async def kn_parser(
    httpx_client: httpx.AsyncClient,
    logger: Logger,
    interval: int) -> list[tuple[str, ...]]:
    """
    Парсер kubnews.ru
    """
    site_url = "https://kubnews.ru/all/?type=news" 
    
    results: list[tuple[str, ...]] = []
    
    try:
        logger.debug("отправляю запрос к %s", site_url)
        
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
                date = '-'.join(date.split(' ')[0].split('.')[::-1])
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.material__content p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(interval)
        
        logger.info("запарсено %d новостей с %s", len(results), site_url) 
    
    except (httpx.HTTPError, httpx.InvalidURL) as e:
        logger.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
            

async def kt_parser(
    httpx_client: httpx.AsyncClient,
    logger: Logger,
    interval: int) -> list[tuple[str, ...]]:
    """
    Парсер для kubantoday.ru
    """
    site_url = "https://kubantoday.ru/allposts/"              
    
    results: list[tuple[str, ...]] = []
    
    try:
        logger.debug("отправляю запрос к %s", site_url)
        
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
                date = '-'.join(date.split(' ')[1].split('.')[::-1])
                            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('article > p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(interval)
        
        logger.info("запарсено %d новостей с %s", len(results), site_url) 
    
    except (httpx.HTTPError, httpx.InvalidURL) as e:
        logger.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        

async def lk_parser(
    httpx_client: httpx.AsyncClient,
    logger: Logger,
    interval: int) -> list[tuple[str, ...]]:
    """
    Парсер livekuban.ru
    """
    site_url = "https://www.livekuban.ru/news"
    
    results: list[tuple[str, ...]] = []
    
    try:
        logger.debug("отправляю запрос к %s", site_url)
        
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)
        
        for article in selector.css("div.node--news"):
            title = article.css('div.node--description span::text').get().strip()
            url = article.css('div.node--description a::attr(href)').get().strip()
            
            date = article.css("div.date::text").get().strip()
            date = '-'.join(date.split(' ')[0].split('.')[::-1])
        
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.article-content > p::text').getall()])
            
            results.append((url, title, descr, date))
            
            await asyncio.sleep(interval)

        logger.info("запарсено %d новостей с %s", len(results), site_url) 
    
    except (httpx.HTTPError, httpx.InvalidURL) as e:
        logger.error("ошибка при парсинге %s: %s", site_url, e)
        
    finally: return results
        

async def parse_many(
    *parsers: Callable[[httpx.AsyncClient, Logger, int], list[tuple[str, ...]]],
    db_path: str,
    logger: Logger,
    interval: int) -> None:
    """
    Запускает переданные парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            parsed_urls: list[str] = []
            
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("SELECT url FROM Articles")
                parsed_urls = list(
                    map(itemgetter(0), db_cursor.fetchall())
                )

            logger.debug("запуск парсеров")
            
            inter_res = await asyncio.gather(
                *map(lambda f: f(httpx_client, logger, interval), parsers)
            )
            
            total_posts: int = sum(map(len, inter_res))
            logger.info("запарсено всего %d новостей", total_posts) 
            
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
                                "INSERT INTO Articles VALUES(?, ?, ?, ?, -1)",
                                (url, title, descr, date)
                            )
                            parsed_urls.append(url) 
                            new_posts += 1
            
            logger.info("в бд добавлено %d новостей", new_posts)
    
    except (sqlite3.OperationalError, sqlite3.Error) as e:
        logger.error("ошибка при добавлении записей: %s", e)


async def parse_all(
    db_path: str,
    logger: Logger,
    interval: int) -> None:
    """
    Запускает все парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            
            parsed_urls: list[str] = []
            
            with sqlite3.connect(db_path) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("SELECT url FROM Articles")
                parsed_urls = list(
                    map(itemgetter(0), db_cursor.fetchall())
                )

            logger.debug("запуск парсеров")
            
            inter_res = await asyncio.gather(
                k24_parser(httpx_client, logger, interval ),
                kn_parser( httpx_client,  logger, interval),
                kt_parser( httpx_client,  logger, interval),
                lk_parser( httpx_client,  logger, interval)
            )
            
            total_posts: int = sum(map(len, inter_res))
            logger.info("запарсено всего %d новостей", total_posts) 
            
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
                                "INSERT INTO Articles VALUES(?, ?, ?, ?, -1)",
                                (url, title, descr, date)
                            )
                            parsed_urls.append(url) 
                            new_posts += 1
            
            logger.info("в бд добавлено %d новостей", new_posts)
    
    except (sqlite3.OperationalError, sqlite3.Error) as e:
        logger.error("ошибка при добавлении записей: %s", e)
    
        
if __name__ == "__main__":

    logger = getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    
    db_path = input("введите путь к БД: ")
        
    asyncio.run(parse_all(db_path="articles.db", logger=logger, interval=1))