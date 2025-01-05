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


class ClusteringDB:
    __db_path: str

    # параметры векторизации:
    __max_df = 0.7
    __min_df = 1
    # параметры кластеризации:
    __eps = 1.17
    __min_samples = 1

    def __init__(self, db_path: str) -> None:
        self.__db_path = db_path

    def run(self):
        with sqlite3.connect(self.__db_path) as db_con:
            db_cursor = db_con.cursor()
            db_cursor.execute("SELECT description FROM Articles")
            descriptions = list(
                map(itemgetter(0), db_cursor.fetchall())
            )
            vectors = self.__make_vectors(descriptions)
            clusters_labels = self.__make_clusters(vectors)
            db_cursor.executemany(
                "update Articles set cluster_n = ? where description = ?",
                [(int(clust_n), descr) for descr, clust_n in zip(descriptions, clusters_labels)]
            )

    def __make_vectors(self, descriptions):
        vectorizer = StemmedTfidfVectorizer(max_df=self.__max_df, min_df=self.__min_df, decode_error="ignore")
        return vectorizer.fit_transform(descriptions)

    def __make_clusters(self, vectors):
        """
        Добавляет номера кластеров к записям таблицы Articles
        """
        dbscan = DBSCAN(eps=self.__eps, min_samples=self.__min_samples)
        dbscan.fit(vectors)
        return dbscan.labels_
