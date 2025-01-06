"""
Flask-приложение

Функции для загрузки данных из бд sqlite и одна страница. 
"""

from flask import Flask, render_template

from controllers.parser_controller import Article
from pre_start import app_controller, start_parsers, stop_parsers

app = Flask(__name__)

@app.route('/')
def index():
    clusters_headers = app_controller.get_clusters_headers()
    clusters_article: list[list[Article]] = [
        app_controller.get_article_by_cluster(article.cluster_n)
        for article in clusters_headers
    ]
    return render_template(
        "index.html", title="Новости",
        headers=clusters_headers,
        articles=clusters_article
    )


if __name__ == "__main__":
    try:
        start_parsers()
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        stop_parsers()
