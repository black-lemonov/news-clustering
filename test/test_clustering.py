from clustering.dbscan import DBSCANAlgorithm
from controllers.clustering_controller import ClusteringController
from db_context.sqlite_context import SQLiteDBContext
from vectorization.stemmed_vectorizer import StemmedVectorizer


def test_clustering():
    db_context = SQLiteDBContext("../resources/articles.db")
    text_vectorizer = StemmedVectorizer()
    clustering_algorithm = DBSCANAlgorithm()
    clustering_controller = ClusteringController(
        db_context,
        text_vectorizer,
        clustering_algorithm
    )
    clustering_controller.add_clusters()
