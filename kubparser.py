import asyncio
import logging
import sqlite3
from httpx import AsyncClient
from scrapy.selector import Selector
from collections import deque


async def k24_parser(httpx_client: AsyncClient):
    '''
    Парсер для kuban24.tv
    '''
    site_url = "https://kuban24.tv/news"
    
    response = await httpx_client.get(site_url)
    
    selector = Selector(text=response.text)
    results = {}
    for article in selector.css('div.news-card'):
        #'published', article.css('div.news-card-date::text').get().strip()
        title = article.css('a.news-card-title::text').get().strip()
        url = article.css('a.news-card-title::attr(href)').get().strip()
        page = await httpx_client.get(url)
        page_selector = Selector(text=page.text)
        descr = ' '.join([p.strip() for p in page_selector.css('div[itemprop="description"] > p::text').getall()])    
        results[url] = title, descr 
    return results
        
        
async def kn_parser(httpx_client: AsyncClient):
    '''
    Парсер kubnews.ru
    '''
    site_url = "https://kubnews.ru/all/?type=news"
    
    response = await httpx_client.get(site_url)
    
    selector = Selector(text=response.text)     
    results = {}
    for article in selector.css('a.card'):
        #'published', article.css('span.card__date::text').get().strip()
        title = article.css('div.card__description::text').get().strip()
        url = "https://kubnews.ru" + article.attrib['href'].strip()
        page = await httpx_client.get(url)
        page_selector = Selector(text=page.text)
        descr = ' '.join([p.strip() for p in page_selector.css('div.material__content p::text').getall()])
        
        results[url] = title, descr
    return results
            

async def kt_parser(httpx_client: AsyncClient):
    '''
    Парсер для kubantoday.ru
    '''
    site_url = "https://kubantoday.ru/allposts/"
    
    response = await httpx_client.get(site_url)
    selector = Selector(text=response.text)                
    results = {}
    for article in selector.css('article'):
        title = article.css('h3 a::text').get().strip()
        url = article.css('h3 a::attr(href)').get().strip()      
        page = await httpx_client.get(url)
        page_selector = Selector(text=page.text)
        descr = ' '.join([p.strip() for p in page_selector.css('article > p::text').getall()])
        results[url] = title, descr
    return results
        

async def lk_parser(httpx_client: AsyncClient):
    '''
    Парсер livekuban.ru
    '''
    site_url = "https://www.livekuban.ru/news"

    response = await httpx_client.get(site_url)

    selector = Selector(text=response.text)
    results = {}
    for article in selector.css("div.node--news"):
        #date = article.css('div.date::text').get().strip()
        title = article.css('div.node--description span::text').get().strip()
        url = article.css('div.node--description a::attr(href)').get().strip()
        page = await httpx_client.get(url)
        page_selector = Selector(text=page.text)
        descr = ' '.join([p.strip() for p in page_selector.css('div.article-content > p::text').getall()])
        
        results[url] = title, descr
    return results
        

async def parse_all(db_name: str):
    '''
    Запускает все парсеры с периодичностью
    и записывает результат их работы в БД
    '''
    async with AsyncClient() as httpx_client:
        parsed_q = deque()
        
        with sqlite3.connect(db_name) as db_con:
            db_cursor = db_con.cursor()
            db_cursor.execute("select url from Articles")
            parsed_q.extendleft(
                map(lambda x: x[0], db_cursor.fetchall())
            )

        inter_res = await asyncio.gather(
            k24_parser(httpx_client), 
            kn_parser(httpx_client),
            kt_parser(httpx_client), 
            lk_parser(httpx_client)
        )
        
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
        
        print(f"парсинг прошел успешно.")
        

if __name__ == "__main__":
    asyncio.run(parse_all("articles.db"))
