from flask import Blueprint, render_template

from flaskr.resources.db import get_db
from flaskr.tasks import run_algorithm_task

bp = Blueprint("news", __name__)

@bp.route("/")
def index():
    run_algorithm_task.delay()
    db = get_db()
    clusters = db.execute(
        'SELECT * FROM cluster ORDER BY first_article_date DESC;'
    ).fetchall()
    return render_template('news/index.html', clusters=clusters)
