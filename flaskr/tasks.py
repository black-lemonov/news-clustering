from celery import shared_task

from flaskr.scripts.run_algorithm import run_algorithm
from flaskr.scripts.run_parsers import run_parsers


@shared_task(ignore_result=True)
def run_parsers_task():
    run_parsers()


@shared_task(ignore_result=True)
def run_algorithm_task():
    run_algorithm()
