from functools import partial
import sqlite3
import scipy as sp
import numpy as np
from typing import Callable
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from typing import Callable, Any

# когда удалять кластеры?

# с какими промежутком парсить новости?

# чтобы это определить надо выполнить парсинг
# всех сайтов и проанализировать полученные данные

# а пока реализация самого алгоритма:

class StemmedTfidfVectorizer(TfidfVectorizer):
    '''
    TF-IDF векторизатор со стеммингом
    '''
    def build_analyzer(self) -> Callable[..., Any] | partial:
        russian_stemmer = SnowballStemmer("russian")
        stop_words = stopwords.words("russian") + list(punctuation)
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: (
            russian_stemmer.stem(w) for w in analyzer(doc)
            if w not in stop_words
        )


def load_from_db(db_path: str) -> list[str]:
    '''
    Загружает данные из бд и сохраняет их в список
    '''
    descr: list[str] = [] 
    with sqlite3.connect(db_path) as db_con:
        db_cursor = db_con.cursor()
        db_cursor.execute("select description from Articles")
        descr = list(map(lambda x: x[0], db_cursor.fetchall()))
    return descr


def vectorize_data(data: list[str]) -> sp.sparse.spmatrix:
    '''
    Векторизует данные и возвращает разряженную матрицу
    '''
    vectorizer = StemmedTfidfVectorizer(max_df=0.5, decode_error="ignore")
    return vectorizer.fit_transform(data)


def make_clusters(vectorized_data: sp.sparse.spmatrix) -> np.ndarray:
    '''
    Кластеризует векторизованные данные, возвращает массив с номерами кластеров
    '''
    km = DBSCAN(eps=1.17, min_samples=1)
    km.fit(vectorized_data)
    return km.labels_


def update_db(db_path: str) -> None:
    '''
    Добавляет номера кластеров к записям бд
    '''
    raw_data = load_from_db("articles.db")
    vectorized_data = vectorize_data(raw_data)
    clusters_labels = make_clusters(vectorized_data)
    
    with sqlite3.connect(db_path) as db_con:
        db_cursor = db_con.cursor()
        for cluster_i, descr in zip(clusters_labels, raw_data):
            db_cursor.execute(
            "update Articles set cluster_n = ? where description = ?",
            (int(cluster_i), descr))
    print("Индексы обновлены успешно.")
    
    
if __name__ == "__main__":
    update_db("articles.db")