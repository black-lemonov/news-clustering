"""
Flask-приложение

Функции для загрузки данных из бд sqlite и одна страница. 
"""

from config import logger_config_path, db_path, parser_timeout, parsers_interval, cleaner_timeout
from flask import Flask, render_template
from clustering import clustering_db
from multiprocessing import Process

from main import logger, repository
from parsing.kubparser import parse_all
import asyncio

from repository import News

app = Flask(__name__)
    

@app.route('/')
def index():

    # # проверка наличия таблицы:
    # check_db(db_path, logger)
    
    # if cleaner_timer.is_alive() == False:
    #     logger.debug("запускаю клинер")
    #
    #     run_cleaner(cleaner_timeout, logger)
    #
    #     logger.debug("клинер завершил работу")
    #
    #     cleaner_timer.start()
    #
    #     logger.debug("запускаю таймер для клинера; жду %d сек.", cleaner_timeout)
    #
    # if parser_timer.is_alive() == False:
    #
    #     logger.debug("запускаю парсер")
    #
    #     asyncio.run(parse_all(db_path, logger, parsers_interval))
    #
    #     logger.debug("парсер завершил работу")
    #
    #     clust_process = Process(
    #         target=clustering_db,
    #         args=(db_path, logger)
    #     )
    #
    #     logger.debug("запускаю процесс с кластеризацией")
    #
    #     clust_process.start()
    #     clust_process.join()
    #
    #     logger.debug("процесс кластеризации завершен")
    #
    #     logger.debug("запускаю таймер для парсера; жду %d сек.", parser_timeout)
    #
    #     parser_timer.start()
    
    # загрузка новостей из бд:
    clusters_headers = repository.get_clusters_headers(db_path, logger)

    clusters_news: list[list[News]] = [
        repository.get_news_by_cluster(news.cluster_n)
        for news in clusters_headers
    ]
        
    return render_template("index.html", title="Новости", headers=clusters_headers, news=clusters_news)


if __name__ == "__main__":
    cleaner_timer.start()
    app.run(debug=True)

