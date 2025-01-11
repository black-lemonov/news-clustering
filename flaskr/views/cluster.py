from flask import Blueprint, render_template, flash, redirect, url_for

from flaskr.resources.db import get_db

bp = Blueprint('cluster', __name__, url_prefix='/cluster')

@bp.route('/<int:cluster_id>')
def show_news_by_cluster(cluster_id):
    db = get_db()
    cluster = db.execute(
        "SELECT * FROM cluster WHERE id = ?;",
        (cluster_id,)
    ).fetchone()
    if cluster is None:
        flash('Ссылка не найдена :(')
        return redirect(url_for('news.index'))
    articles = db.execute(
        "SELECT * FROM article WHERE cluster_id = ?;",
        (cluster_id,)
    )

    return render_template(
        'cluster/show_news_by_cluster.html',
        cluster=cluster,
        articles_by_cluster=articles
    )
