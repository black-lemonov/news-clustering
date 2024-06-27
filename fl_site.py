"""
Flask-приложение

Функции для загрузки данных из бд sqlite и одна страница. 
"""

from flask import Flask, render_template
from logging import getLogger, Logger
from clustering import clustering_db
from kubparser import parse_all
from threading import Thread
import logging.config
import asyncio
import sqlite3
import time
import json


logging.getLogger("werkzeug").disabled = True

logger = None

try:
    with open("logging.conf") as file:
        config = json.load(file)
    
    logging.config.dictConfig(config)
    logger = getLogger()

except FileNotFoundError:
    print("ошибка при загрузке конфигурации логгера")


app = Flask(__name__)
    
timeout: int = 3600 # сек

days_limit: int = 2 # дней

db_path = "articles.db"

parser_timer: Thread = Thread(
    target=time.sleep,
    args=(timeout,),
    daemon=True
)

cleaner_timer: Thread = Thread(
    target=time.sleep,
    args=(days_limit * 24 * 3600,), 
    daemon=True
)

@app.route('/')
def index():
    
    if cleaner_timer.is_alive() == False:
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
        
        finally:
            logger.debug("запускаю таймер; жду %d дней", days_limit)
            cleaner_timer.start()
    
    if parser_timer.is_alive() == False:
        asyncio.run(parse_all(db_path, logger))
        clustering_db(db_path, logger)
        logger.debug("запускаю таймер; жду %d сек.", timeout)
        parser_timer.start()
    
    # загрузка новостей из бд:
    news: dict[int, tuple[str, ...]] = dict()   
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, cluster_n FROM Articles")
            for post in cursor.fetchall():
                url, title, *_, cluster_n = cluster_n = post
                
                if news.get(cluster_n) is None:
                    news[cluster_n] = [(url, title)]
                else:
                    news[cluster_n].append((url, title))
            
            logger.info("загружено %d новостей", len(news))
    
    except sqlite3.OperationalError as e:
        logger.error("ошибка при загрузке записей: %s", e)       
    
    finally:
        return render_template("index.html", title="Новости", clusters=list(news.values()))


if __name__ == "__main__":
    logger.debug("запуск приложения")
    cleaner_timer.start()
    logger.debug("запускаю таймер; жду %d дней", days_limit)
    app.run(debug=True)

