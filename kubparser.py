"""
Парсеры кубанских новостных сайтов

Содержит асинхронные методы для парсинга таких сайтов, как: kuban24.tv, kubnews.ru, kubantoday.ru и livekuban.ru.
Методы возвращают результат парсинга в виде словаря, содержащего ссылку на статью, её заголовок и полный текст.

Главная функция для запуска всех парсеров - parse_all. Записывает данные в базу данных sqlite.  
"""

from scrapy.selector import Selector
from collections import deque
from typing import Callable
from logging import Logger
import sqlite3
import asyncio
import httpx


async def k24_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> dict[str, tuple[str, ...]]:
    """
    Парсер для kuban24.tv
    """
    site_url = "https://kuban24.tv/news"
    
    results = {}
    
    try:
        response = await httpx_client.get(site_url)
    
        selector = Selector(text=response.raise_for_status().text)

        for article in selector.css('div.news-card'):
            title = article.css('a.news-card-title::text').get().strip()
            url = article.css('a.news-card-title::attr(href)').get().strip()
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div[itemprop="description"] > p::text').getall()])    
            
            results[url] = title, descr
        
        if log: log.info(f"Парсинг {site_url}; запарсено новостей: {len(results)}.") 
    
    except httpx.NetworkError as exc:
        if log: log.error(f"Сетевая ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.InvalidURL:
        if log: log.error(f"Ошибка адреса URL для {exc.request.url} - {exc}")
    
    except httpx.ConnectTimeout:
        if log: log.error(f"Ошибка времени подключения для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.HTTPError as exc:
        if log: log.error(f"HTTP ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    finally: return results
        
    
        
        
async def kn_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> dict[str, tuple[str, ...]]:
    """
    Парсер kubnews.ru
    """
    site_url = "https://kubnews.ru/all/?type=news" 
    
    results = {}
    
    try:
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)    
        
        for article in selector.css('a.card'):
            title = article.css('div.card__description::text').get().strip()
            url = "https://kubnews.ru" + article.attrib['href'].strip()
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.material__content p::text').getall()])
            
            results[url] = title, descr
        
        if log: log.info(f"Парсинг {site_url}; запарсено новостей: {len(results)}.")
    
    except httpx.NetworkError as exc:
        if log: log.error(f"Сетевая ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.InvalidURL:
        if log: log.error(f"Ошибка адреса URL для {exc.request.url} - {exc}")
    
    except httpx.ConnectTimeout:
        if log: log.error(f"Ошибка времени подключения для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.HTTPError as exc:
        if log: log.error(f"HTTP ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    finally: return results
            

async def kt_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> dict[str, tuple[str, ...]]:
    """
    Парсер для kubantoday.ru
    """
    site_url = "https://kubantoday.ru/allposts/"              
    
    results = {}
    
    try:
        response = await httpx_client.get(site_url)
        
        selector = Selector(text=response.raise_for_status().text)  
        
        for article in selector.css('article'):
            title = article.css('h3 a::text').get().strip()
            url = article.css('h3 a::attr(href)').get().strip()      
            
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('article > p::text').getall()])
            
            results[url] = title, descr
        
        if log: log.info(f"Парсинг {site_url}; запарсено новостей: {len(results)}.") 
    
    except httpx.NetworkError as exc:
        if log: log.error(f"Сетевая ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.InvalidURL:
        if log: log.error(f"Ошибка адреса URL для {exc.request.url} - {exc}")
    
    except httpx.ConnectTimeout:
        if log: log.error(f"Ошибка времени подключения для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.HTTPError as exc:
        if log: log.error(f"HTTP ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    finally: return results
        

async def lk_parser(
    httpx_client: httpx.AsyncClient,
    log: Logger = None) -> dict[str, tuple[str, ...]]:
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
        
            page = await httpx_client.get(url)
            page_selector = Selector(text=page.text)
            
            descr = ' '.join([p.strip() for p in page_selector.css('div.article-content > p::text').getall()])
            
            results[url] = title, descr
        
        if log: log.info(f"Парсинг {site_url}; запарсено новостей: {len(results)}.")
    
    except httpx.NetworkError as exc:
        if log: log.error(f"Сетевая ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.InvalidURL:
        if log: log.error(f"Ошибка адреса URL для {exc.request.url} - {exc}")
    
    except httpx.ConnectTimeout:
        if log: log.error(f"Ошибка времени подключения для {exc.request.url} - {exc}", exc_info=1)
    
    except httpx.HTTPError as exc:
        if log: log.error(f"HTTP ошибка для {exc.request.url} - {exc}", exc_info=1)
    
    finally: return results
        

async def parse_many(
    *parsers: Callable[[httpx.AsyncClient, Logger | None], dict[str, tuple[str, ...]]],
    db_name: str,
    log: Logger = None) -> None:
    """
    Запускает переданные парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            parsed_q = deque()
            
            with sqlite3.connect(db_name) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("select url from Articles")
                parsed_q.extendleft(
                    map(lambda x: x[0], db_cursor.fetchall())
                )

            inter_res = await asyncio.gather(
                *map(lambda f: f(httpx_client, log), parsers)
            )
            
            total_posts: int = sum(map(len, inter_res))
            if log: log.info(f"Парсинг {len(parsers)} сайтов; кол-во новостей: {total_posts}.") 
            
            new_posts: int = 0
            with sqlite3.connect(db_name) as db_con:
                db_cursor = db_con.cursor()
                for news in inter_res:
                    for url, tupl in news.items():
                        text, descr = tupl
                        if "ТОП" in text:
                            continue
                        if descr == "" or text == "" or url == "":
                            continue
                        if url not in parsed_q:
                            db_cursor.execute(
                                "insert into Articles values(?, ?, ?, -1)",
                                (url, text, descr)
                            )
                            parsed_q.appendleft(url) 
                            new_posts += 1
            
            if log: log.info(f"В {db_name} добавлено {new_posts} новостей.")
    
    except sqlite3.OperationalError as exc:
        if log: log.error(f"Ошибка SQL-запроса - {exc}", exc_info=1)


async def parse_all(
    db_name: str,
    log: Logger = None) -> None:
    """
    Запускает все парсеры и записывает результат их работы в БД
    """
    try:
        async with httpx.AsyncClient() as httpx_client:
            parsed_q = deque()
            
            with sqlite3.connect(db_name) as db_con:
                db_cursor = db_con.cursor()
                db_cursor.execute("select url from Articles")
                parsed_q.extendleft(
                    map(lambda x: x[0], db_cursor.fetchall())
                )

            inter_res = await asyncio.gather(
                k24_parser(httpx_client, log),
                kn_parser(httpx_client, log),
                kt_parser(httpx_client, log),
                lk_parser(httpx_client, log)
            )
            
            total_posts: int = sum(map(len, inter_res))
            if log: log.info(f"Парсинг ВСЕХ сайтов; кол-во новостей: {total_posts}.") 
            
            new_posts: int = 0
            with sqlite3.connect(db_name) as db_con:
                db_cursor = db_con.cursor()
                for news in inter_res:
                    for url, tupl in news.items():
                        text, descr = tupl
                        if "ТОП" in text:
                            continue
                        if descr == "" or text == "" or url == "":
                            continue
                        if url not in parsed_q:
                            db_cursor.execute(
                                "insert into Articles values(?, ?, ?, -1)",
                                (url, text, descr)
                            )
                            parsed_q.appendleft(url) 
                            new_posts += 1
            
            if log: log.info(f"В {db_name} добавлено {new_posts} новостей.")
    
    except sqlite3.OperationalError as exc:
        if log: log.error(f"Ошибка SQL-запроса - {exc}", exc_info=1)
    
        
if __name__ == "__main__":
    asyncio.run(parse_all(db_name="articles copy.db"))
