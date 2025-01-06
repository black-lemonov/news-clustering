from sklearn.cluster import DBSCAN

from clustering.abc_algorithm import TextClusteringAlgorithm


class DBSCANAlgorithm(TextClusteringAlgorithm):
    __eps = 1.17
    __min_samples = 1

    __dbscan: DBSCAN

    def __init__(self):
        self.__dbscan = DBSCAN(eps=self.__eps, min_samples=self.__min_samples)

    def make_clusters(self, any_data):
        self.__dbscan.fit(any_data)
        return self.__dbscan.labels_