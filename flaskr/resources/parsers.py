from flask import current_app, g

from flaskr.news_parser import NewsParser


def get_parsers():
    if 'parsers' not in g:
        g.parsers = [
            NewsParser(**config)
            for config in current_app.config['PARSERS']
        ]

    return g.parsers