import logging
import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config["DATABASE"] = os.path.join(app.instance_path, 'flaskr.sqlite')

    app.logger.setLevel(logging.INFO)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr.resources import db
    db.init_app(app)

    from flaskr import celery_init
    celery_init.celery_init_app(app)

    from flaskr.commands import init_db_command
    init_db_command.init_app(app)

    from flaskr.commands import run_algorithm_command
    run_algorithm_command.init_app(app)

    from flaskr.commands import run_parsers_command
    run_parsers_command.init_app(app)

    from flaskr.views import cluster
    app.register_blueprint(cluster.bp)

    from flaskr.views import news
    app.register_blueprint(news.bp)
    app.add_url_rule('/', endpoint='index')

    return app
