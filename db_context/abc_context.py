from abc import ABC, abstractmethod

from dto.article import Article


class DBContext(ABC):
    @abstractmethod
    def insert(self, values: tuple[str, str, str, str]) -> None:
        pass

    @abstractmethod
    def delete_where_days_limit(self, days_limit: int) -> None:
        pass

    @abstractmethod
    def select_min_date_by_clusters(self) -> list[Article]:
        pass

    @abstractmethod
    def select_by_cluster(self, cluster_n: int) -> list[Article]:
        pass

    @abstractmethod
    def select_descriptions(self) -> list[str]:
        pass

    @abstractmethod
    def set_cluster_n_where_description(self, clusters: list[int], descriptions: list[str]) -> None:
        pass