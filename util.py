from repository import News


def news_to_tuple(news: News) -> tuple[str, str, str]:
    return news.url, news.title, news.date