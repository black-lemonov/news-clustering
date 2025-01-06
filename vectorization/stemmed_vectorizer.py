from string import punctuation

from nltk import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from vectorization.abc_vectorizer import TextVectorizer


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


class StemmedVectorizer(TextVectorizer):
    __max_df = 0.7
    __min_df = 1

    __vectorizer: _StemmedTfidfVectorizer

    def __init__(self, ) -> None:
        self.__vectorizer = _StemmedTfidfVectorizer(
            max_df=self.__max_df,
            min_df=self.__min_df,
            decode_error="ignore"
        )

    def make_vectors(self, any_data) -> object:
        return self.__vectorizer.fit_transform(any_data)
