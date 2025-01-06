from icecream import ic

from clustering.abc_algorithm import TextClusteringAlgorithm
from db_context.sqlite_context import DBContext
from vectorization.abc_vectorizer import TextVectorizer


class ClusteringController:
    __db_context: DBContext
    __text_vectorizer: TextVectorizer
    __clustering_algorithm: TextClusteringAlgorithm

    def __init__(
            self,
            db_context: DBContext,
            text_vectorizer: TextVectorizer,
            clustering_algorithm: TextClusteringAlgorithm
    ):
        self.__db_context = db_context
        self.__text_vectorizer = text_vectorizer
        self.__clustering_algorithm = clustering_algorithm

    def add_clusters(self) -> None:
        descriptions = self.__db_context.select_descriptions()
        vectors = self.__text_vectorizer.make_vectors(descriptions)
        clusters_labels = self.__clustering_algorithm.make_clusters(vectors)
        self.__db_context.set_cluster_n_where_description(
            clusters_labels, descriptions
        )