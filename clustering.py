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
from logging import Logger, getLogger
import logging.config
import sqlite3
import scipy as sp
import numpy as np
import json

# когда удалять кластеры?

# с какими промежутком парсить новости?

# чтобы это определить надо выполнить парсинг
# всех сайтов и проанализировать полученные данные

# а пока реализация самого алгоритма:

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


def clustering_db(db_path: str, log: Logger = None) -> None:
    """
    Добавляет номера кластеров к записям таблицы Articles
    """
    # параметры векторизации:
    max_df = 0.7
    min_df = 1
    # параметры кластеризации:
    eps = 1.15
    min_samples = 1
    
    try:
        with sqlite3.connect(db_path) as db_con:
            db_cursor = db_con.cursor()
            db_cursor.execute(
                "select description from Articles;"
            )
            if log: log.info("запрос к бд")
            descriptions = list(
                map(itemgetter(0), db_cursor.fetchall())
            )
            
            vectorizer = StemmedTfidfVectorizer(max_df=max_df, min_df=min_df, decode_error="ignore")
            vectors = vectorizer.fit_transform(descriptions)
            
            if log: log.info("векторизация; параметры: max_df = %f , min_df = %f", max_df, min_df)
    
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            dbscan.fit(vectors)
            clust_labels = dbscan.labels_ 
            if log:
                log.info("кластеризация; параметры: eps = %f , min_samples = %d ; получено %d кластеров", eps, min_samples, clust_labels)
            
            db_cursor.executemany(
                "update Articles set cluster_n = ? where description = ?",
                [(clust_n, descr) for descr, clust_n in zip(descriptions, clust_labels)]
            )
            
            if log: log.info("обновлено %d записей", len(db_cursor.fetchall()))
                
    except sqlite3.OperationalError as e:
        if log: log.error("ошибка при кластеризации: %s", e)
    except sqlite3.InterfaceError as e:
        if log: log.error("ошибка при кластеризации: %s", e)
    except ValueError as e:
        if log: log.error("ошибка при кластеризации: %s", e)
    
    
if __name__ == "__main__":
    
    logger = logging.getLogger(__name__)
    logging.basicConfig()
    
    # insert_clusters("articles2.db", log=logger)
    
    