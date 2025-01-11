import click

from flaskr.resources.db import init_db, close_db


@click.command('init-db')
def init_db_command():
    """Пересоздать базу данных"""
    init_db()
    click.echo('БД создана.')

def init_app(app):
    app.cli.add_command(init_db_command)