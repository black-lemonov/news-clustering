import asyncio
import logging
import sqlite3
from httpx import AsyncClient
from scrapy.selector import Selector
from collections import deque

class KubParser:
    '''
    Парсеры для сайтов новостей
    '''
    
    def __init__(self, httpx_client: AsyncClient):
        self._parsed_q = deque()
        self._httpx_client = httpx_client
    
    
    async def k24_parser(self):
        '''
        Парсер для kuban24.tv
        '''
        
        site_url = "https://kuban24.tv/news"
        
        response = await self._httpx_client.get(site_url)
        
        selector = Selector(text=response.text)
        results = {}
        for article in selector.css('div.news-card'):
            #'published', article.css('div.news-card-date::text').get().strip()
            title = article.css('a.news-card-title::text').get().strip()
            url = article.css('a.news-card-title::attr(href)').get().strip()
            results[url] = title
        return results
            
            
    async def kn_parser(self):
        '''
        Парсер kubnews.ru
        '''

        site_url = "https://kubnews.ru/all/?type=news"
        
        response = await self._httpx_client.get(site_url)
        
        selector = Selector(text=response.text)     
        results = {}
        for article in selector.css('a.card'):
            #'published', article.css('span.card__date::text').get().strip()
            title = article.css('div.card__description::text').get().strip()
            url = "https://kubnews.ru" + article.attrib['href'].strip()
            results[url] = title
        return results
                

    async def kt_parser(self):
        '''
        Парсер для kubantoday.ru
        '''
        
        site_url = "https://kubantoday.ru/allposts/"
        
        response = await self._httpx_client.get(site_url)

        selector = Selector(text=response.text)                
        results = {}
        for article in selector.css('article'):
            #published = article.css('div.feed-news-full__card-time::text').get().strip()
            title = article.css('h3 a::text').get().strip()
            url = article.css('h3 a::attr(href)').get().strip()
            results[url] = title
        return results
            

    async def lk_parser(self):
        '''
        Парсер livekuban.ru
        '''
        
        site_url = "https://www.livekuban.ru/news"

        response = await self._httpx_client.get(site_url)

        selector = Selector(text=response.text)
        results = {}
        for article in selector.css("div.node--news"):
            #date = article.css('div.date::text').get().strip()
            title = article.css('div.node--description span::text').get().strip()
            url = article.css('div.node--description a::attr(href)').get().strip()
            results[url] = title
        return results
            

    async def all(self, db_name, timeout = 3600):
        '''
        Парсит данные сразу из всех источников
        '''
        
        with sqlite3.connect(db_name) as db_con:
            db_cursor = db_con.cursor()
            db_cursor.execute("select url from Articles")
            self._parsed_q.extendleft(
                map(lambda x: x[0], db_cursor.fetchall())
            )
        
        while True:
            try:
                inter_res = await asyncio.gather(
                    self.k24_parser(), 
                    self.kn_parser(),
                    self.kt_parser(), 
                    self.lk_parser()
                )
            except:
                logging.exception(f"ошибка в Parser.all")
                await asyncio.sleep(timeout:=timeout * 2)
                logging.info(f"timeout увеличен до {timeout} сек.")
                continue
            
            with sqlite3.connect(db_name) as db_con:
                db_cursor = db_con.cursor()
                for news in inter_res:
                    for url, text in news.items():
                        if url not in self._parsed_q:
                            db_cursor.execute(
                                "insert into Articles values(?, ?)",
                                (url, text,)
                            )
                            self._parsed_q.appendleft(url)                    
            
            print(f"парсинг прошел успешно жду {timeout} сек.")
            logging.info(f"парсинг прошел успешно жду {timeout} сек.")
            await asyncio.sleep(timeout)
        
    
asyncio.run(KubParser(AsyncClient()).all("articles.db"))
