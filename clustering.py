"""
Кластеризация содержимого бд

Содержит методы для загрузки данных из sqlite, класс для векторизации текстовых данных и метод для их кластеризации.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.cluster import DBSCAN
from nltk.corpus import stopwords
from typing import Callable, Any
from string import punctuation
from operator import itemgetter
from functools import partial
from logging import Logger
import logging.config
import sqlite3


class StemmedTfidfVectorizer(TfidfVectorizer):
    """
    TF-IDF векторизатор со стеммингом
    """
    def build_analyzer(self) -> Callable[..., Any] | partial:
        russian_stemmer = SnowballStemmer("russian")
        stop_words = stopwords.words("russian") + list(punctuation)
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: (
            russian_stemmer.stem(w) for w in analyzer(doc)
            if w not in stop_words
        )


def clustering_db(db_path: str, logger: Logger) -> None:
    """
    Добавляет номера кластеров к записям таблицы Articles
    """
    # параметры векторизации:
    max_df = 0.7
    min_df = 1
    # параметры кластеризации:
    eps = 1.17
    min_samples = 1
    
    try:
        with sqlite3.connect(db_path) as db_con:
            db_cursor = db_con.cursor()
            
            logger.debug("загрузка новостей для векторизации")
            
            db_cursor.execute("SELECT description FROM Articles")
            
            logger.debug("новости загружены")
            
            descriptions = list(
                map(itemgetter(0), db_cursor.fetchall())
            )
            
            logger.debug("векторизация новостей")
            
            vectorizer = StemmedTfidfVectorizer(max_df=max_df, min_df=min_df, decode_error="ignore")
            vectors = vectorizer.fit_transform(descriptions)
            
            logger.debug("векторизация завершена")
            
            logger.debug("кластеризация новостей")
    
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            dbscan.fit(vectors)
            clust_labels = dbscan.labels_ 
            
            logger.info("получено %d кластеров", len(set(clust_labels)))
            
            logger.debug("обновление записей бд")
            
            db_cursor.executemany(
                "update Articles set cluster_n = ? where description = ?",
                [(int(clust_n), descr) for descr, clust_n in zip(descriptions, clust_labels)]
            )
            
            logger.info("обновлено %d записей", len(db_cursor.fetchall()))
                
    except sqlite3.OperationalError | sqlite3.InterfaceError | ValueError as e:
        logger.error("ошибка при кластеризации: %s", e)
        
    except ValueError as e:
        logger.error("ошибка при кластеризации: %s", e)
    
    
if __name__ == "__main__":
    
    logger = logging.getLogger(__name__)
    logging.basicConfig()
    
    db_path = input("введите путь к БД")
    
    clustering_db(db_path, logger)
    
    