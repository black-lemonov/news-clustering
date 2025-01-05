"""
Flask-приложение

Функции для загрузки данных из бд sqlite и одна страница. 
"""

from flask import Flask, render_template

from pre_start import repository, start_parsers, stop_parsers, try_create_db

from repository import News
from util import news_to_tuple

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
    clusters_headers = repository.get_clusters_headers()
    clusters_news: list[list[News]] = [
        repository.get_news_by_cluster(news.cluster_n)
        for news in clusters_headers
    ]
    return render_template(
        "index.html", title="Новости",
        headers=[
            news_to_tuple(news)
            for news in clusters_headers
        ],
        news=[
            [
                news_to_tuple(news)
                for news in news_list
            ]
            for news_list in clusters_news
        ]
    )


if __name__ == "__main__":
    # cleaner_timer.start()
    try:
        try_create_db()
        start_parsers()
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        stop_parsers()
