import os

import nltk
from dotenv import load_dotenv

load_dotenv()
nltk.download('stopwords')

SECRET_KEY=os.getenv('SECRET_KEY')

PARSERS = [
  {
    "site_url": "https://kuban24.tv/news",
    "article_selector": "div.news-card",
    "title_selector": "a.news-card-title::text",
    "url_selector": "a.news-card-title::attr(href)",
    "date_selector": "div.news-card-head div.news-card-date::text",
    "content_selector": "div[itemprop=\"description\"] > p::text",
    "stop_words": [],
    "parse_interval_sec": 10.0,
    "articles_buffer_size": 30
  },
  {
    "site_url": "https://www.livekuban.ru/news",
    "article_selector": "div.node--news",
    "title_selector": "div.node--description span::text",
    "url_selector": "div.node--description a::attr(href)",
    "date_selector": "div.date::text",
    "content_selector": "div.article-content > p::text",
    "stop_words": [],
    "parse_interval_sec": 10.0,
    "articles_buffer_size": 30
  }
]

CELERY = {
  "broker_url": "amqp://user:123@localhost:5672/myvhost",
  "timezone": "Europe/Moscow",
  "beat_schedule": {
      "run-parsers-every-hour": {
          "task": "flaskr.tasks.run_parsers_task",
          "schedule": 3600.0
      }
  }
}