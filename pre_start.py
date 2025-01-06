import nltk

from controllers.app_controller import AppController

from start_parsers import scheduler, db_context

nltk.download('stopwords')

app_controller = AppController(db_context)

def start_parsers():
    scheduler.start()

def stop_parsers():
    scheduler.shutdown()

if __name__ == '__main__':
    start_parsers()
