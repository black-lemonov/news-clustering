"""
Flask-приложение

Функции для загрузки данных из бд sqlite и одна страница. 
"""

from config import logger_config_path, db_path, parser_timeout, parsers_interval, cleaner_timeout
from flask import Flask, render_template
from logging import getLogger, Logger
from clustering import clustering_db
from multiprocessing import Process
from kubparser import parse_all
from functools import lru_cache
from threading import Thread
import logging.config
import asyncio
import sqlite3
import time
import json


app = Flask(__name__)

parser_timer: Thread = Thread(
    target=time.sleep,
    args=(parser_timeout,),
    daemon=True
)

cleaner_timer: Thread = Thread(
    target=time.sleep,
    args=(cleaner_timeout,), 
    daemon=True
)

@lru_cache(maxsize=1)
def check_db(db_path: str, logger: Logger) -> None:
    """
    Проверяет есть ли в базе данных по переданному пути таблица Articles,\n
    если нет создает в ней эту таблицу с полями: url, title, description, date, cluster_n\n
    если не существует базы данных по переданному пути - raise sqlite3.OperationalError
    """
    try:
        logger.debug("проверка наличия таблицы Articles: подключение к бд")
        with sqlite3.connect(db_path) as db_con:
            db_cursor = db_con.cursor()
            logger.debug("проверка наличия таблицы Articles: выполнение запроса")
            db_cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "Articles" (
                    "url"	TEXT,
                    "title"	TEXT,
                    "description"	TEXT,
                    "date"	TEXT,
                    "cluster_n"	INTEGER,
                    PRIMARY KEY("url")
                )
                """
            )
            
    except sqlite3.OperationalError as e:
        logger.error("ошибка при проверке: %s", e)
        raise sqlite3.OperationalError(e) 
    
    else: logger.debug("проверка выполнена успешно") 
           
            
@lru_cache(maxsize=1)
def get_logger(config_path: str) -> Logger:
    """
    Загружает логгер по конфиг файлу
    """
    try:
        with open(config_path) as file:
            config = json.load(file)
        
        logging.config.dictConfig(config)
        logger = getLogger()

    except FileNotFoundError as e:
        raise FileNotFoundError("ошибка при загрузке логгера: " + e.strerror)

    else:
        print("загрузка логгера выполнена успешно")
        return logger


def run_cleaner(days_limit: int, logger: Logger) -> None:
    """
    Удаляет записи добавленные > days_limit дней назад
    """
    try:
        with sqlite3.connect(db_path) as db_con:
            db_cursor = db_con.cursor()
            db_cursor.execute(
                f"DELETE FROM Articles WHERE julianday(date) - julianday(date('now')) > ?",
                (days_limit,)
            )
            logger.info("прошло %d дней: удалено %d записей", days_limit, len(db_cursor.fetchall()))
    
    except sqlite3.OperationalError as e:
        logger.error("ошибка при удалении записей: %s", e)
        

def get_clusters_headers(
    db_path: str,
    logger: Logger) -> list[tuple[str, ...]]:
    """
    Запрос к бд: извлечение заголовков кластеров (cluster_n, title, date)
    """
    headers: list[tuple[str, ...]] = [] # (cluster_n, title, date)
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cluster_n, title, min(date)
                FROM Articles
                GROUP BY cluster_n
                """
            )
            headers = cursor.fetchall()

            logger.info("извлечено %d заголовков кластеров", len(headers))
    
    except sqlite3.OperationalError as e:
        logger.error("ошибка при загрузке записей: %s", e)
        
    finally: return headers
    
    
def get_news_by_cluster(
    db_path: str,
    clust_n: int,
    logger: Logger) -> list[tuple[str, ...]]:
    """
    Запрос к бд: извлечение списка новостей по номеру кластера (url, title, date)
    """
    news: list[tuple[str, ...]] = []    # (url, title, date)
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT url, title, date FROM Articles
                WHERE cluster_n = ?
                """,
                (clust_n,)
            )
            
            format = lambda date: '.'.join(date.split('-')[::-1]) 
            
            news = [(url, title, format(date)) for url, title, date in cursor.fetchall()] 
    
    except sqlite3.OperationalError as e:
        logger.error("ошибка при загрузке записей: %s", e)
        
    finally: return news
    

@app.route('/')
def index():
    
    # загрузка логгера:
    logger = get_logger(logger_config_path)
    
    # проверка наличия таблицы:
    check_db(db_path, logger)
    
    if cleaner_timer.is_alive() == False:
        logger.debug("запускаю клинер")
        
        run_cleaner(cleaner_timeout, logger)
        
        logger.debug("клинер завершил работу")
        
        cleaner_timer.start()
        
        logger.debug("запускаю таймер для клинера; жду %d сек.", cleaner_timeout)
    
    if parser_timer.is_alive() == False:
        
        logger.debug("запускаю парсер")
        
        asyncio.run(parse_all(db_path, logger, parsers_interval))
        
        logger.debug("парсер завершил работу")
        
        clust_process = Process(
            target=clustering_db,
            args=(db_path, logger)
        )
        
        logger.debug("запускаю процесс с кластеризацией")
        
        clust_process.start()
        clust_process.join()
        
        logger.debug("процесс кластеризации завершен")
        
        logger.debug("запускаю таймер для парсера; жду %d сек.", parser_timeout)
        
        parser_timer.start()
    
    # загрузка новостей из бд:
    
    logger.debug("извлекаю заголовки кластеров")
    
    clusters_headers = get_clusters_headers(db_path, logger)
    
    logger.debug("заголовки кластеров извлечены")
    
    logger.debug("извлекаю новости по кластерам")
    
    clusters_news: list[list[tuple[str, ...]]] = [
        get_news_by_cluster(db_path, clust_n, logger)
        for clust_n, _, _ in clusters_headers
    ]
        
    logger.debug("новости по кластерам извлечены")
    
    return render_template("index.html", title="Новости", headers=clusters_headers, news=clusters_news)


if __name__ == "__main__":
    cleaner_timer.start()
    app.run(debug=True)

