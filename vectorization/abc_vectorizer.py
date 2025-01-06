from abc import abstractmethod, ABC


class TextVectorizer(ABC):
    @abstractmethod
    def make_vectors(self, any_data) -> object:
        pass