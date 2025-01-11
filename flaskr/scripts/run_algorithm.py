from string import punctuation

from nltk import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

from flaskr.resources.db import get_db


MAX_DF = 0.7
MIN_DF = 1
EPS = 1.17
MIN_SAMPLES = 1


class _StemmedTfidfVectorizer(TfidfVectorizer):
    """
    TF-IDF векторизатор со стеммингом
    """
    def build_analyzer(self):
        russian_stemmer = SnowballStemmer("russian")
        stop_words = stopwords.words("russian") + list(punctuation)
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: (
            russian_stemmer.stem(w) for w in analyzer(doc)
            if w not in stop_words
        )


def run_algorithm():
    db = get_db()
    rows = db.execute(
        "SELECT url, title, content FROM article;"
    ).fetchall()

    vectorizer = _StemmedTfidfVectorizer(
        max_df=MAX_DF,
        min_df=MIN_DF,
        decode_error="ignore"
    )
    vectors = vectorizer.fit_transform([row["content"] for row in rows])

    dbscan = DBSCAN(
        eps=EPS,
        min_samples=MIN_SAMPLES
    )
    dbscan.fit(vectors)
    del vectors

    with db:
        # удалить все старые кластеры
        db.execute(
            "DELETE FROM cluster;"
        )

        # TODO: сделать нормальную саммаризацию
        # создать кластеры но без дат
        # TODO: применить kmeans для поисков центров
        clusters_inserted = set()
        for i, cluster_id in enumerate(dbscan.labels_):
            if cluster_id in clusters_inserted:
                continue
            db.execute(
                "INSERT INTO cluster (id, title, summary) VALUES (:id, :title, :summary);",
                {
                    "id": int(cluster_id),
                    "title": rows[i]["title"],
                    "summary": rows[i]["title"]
                }
            )
            clusters_inserted.add(cluster_id)

        # добавить к статьям номера их кластеров
        db.executemany(
            "UPDATE article SET cluster_id = :cluster_id WHERE url = :url;",
            [
                {
                    "url": row["url"],
                    "cluster_id": int(cluster_id)
                }
                for row, cluster_id in zip(rows, dbscan.labels_)
            ]
        )

        # добавить к кластерам даты
        db.execute(
            """UPDATE cluster SET
            first_article_date = (SELECT MIN(date) FROM article WHERE cluster_id = id),
            last_article_date = (SELECT MAX(date) FROM article WHERE cluster_id = id);"""
        )

    del rows
    del dbscan
