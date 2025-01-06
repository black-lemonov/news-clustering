from abc import ABC, abstractmethod


class TextClusteringAlgorithm(ABC):
    @abstractmethod
    def make_clusters(self, any_data) -> object:
        pass