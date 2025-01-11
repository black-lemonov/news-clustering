import click
from flask import Flask

from flaskr.scripts.run_algorithm import run_algorithm


@click.command("run-algorithm")
def run_algorithm_command():
    click.echo("Запускаю алгоритм...")
    run_algorithm()
    click.echo("Алгоритм выполнен.")


def init_app(app: Flask):
    app.cli.add_command(run_algorithm_command)