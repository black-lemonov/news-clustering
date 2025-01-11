import click
from flask import Flask

from flaskr.scripts.run_parsers import run_parsers


@click.command('run-parsers')
def run_parsers_command():
    click.echo("Запускаю парсеры...")
    run_parsers()
    click.echo("Парсинг завершен.")


def init_app(app: Flask):
    app.cli.add_command(run_parsers_command)