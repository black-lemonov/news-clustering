from flask import Flask, render_template
from clustering import update_db
from kubparser import parse_all
import datetime
import sqlite3
import asyncio

last_run_time = None
db_path = "articles.db"

app = Flask(__name__)

def get_clusters_from_db(db_path: str) -> list[list[list[str]]]:
    '''
    Извлекает новости из бд, возвращает список новостей
    '''
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, text, cluster_n FROM Articles")
        news = dict()
        for post in cursor.fetchall():
            url = post[0]
            text = post[1]
            cluster_n = post[2]
            if news.get(cluster_n) is None:
                news[cluster_n] = [[url, text]]
            else:
                news[cluster_n].append([url, text])
    
    return list(news.values())


@app.route('/')
def index():
    global db_path, last_run_time
    current_time = datetime.datetime.now()
    if last_run_time is None or (current_time - last_run_time).total_seconds() >= 3600:
        asyncio.run(parse_all(db_path))
        update_db(db_path)
        last_run_time = current_time
    news = get_clusters_from_db(db_path)
    return render_template('index.html', title="Новости", clusters = news)


if __name__ == "__main__":
    app.run(debug=True)


