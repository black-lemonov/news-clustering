import pytest

from clustering.dbscan import DBSCANAlgorithm
from controllers.clustering_controller import ClusteringController
from vectorization.stemmed_vectorizer import StemmedVectorizer


@pytest.fixture
def text_vectorizer():
    yield StemmedVectorizer()

@pytest.fixture
def clustering_algorithm():
    yield DBSCANAlgorithm()

@pytest.fixture
def clustering_controller(db_context, text_vectorizer, clustering_algorithm):
    yield ClusteringController(db_context, text_vectorizer, clustering_algorithm)

def test_add_clusters(clustering_controller):
    clusters_before = clustering_controller.count_clusters()
    clustering_controller.add_clusters()
    clusters_after = clustering_controller.count_clusters()
    assert clusters_before < clusters_after
