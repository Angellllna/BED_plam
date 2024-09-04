import abc

from api.algorithm.constants import NGRAM_SIZE, TF_IDF_VECTORIZER
from api.algorithm.imports import *


def generate_n_grams(text, n):
    words = word_tokenize(text)
    n_grams = ngrams(words, n)
    return Counter(n_grams)


def jaccard_similarity(source_ngrams, target_ngrams):
    source_set = set(source_ngrams)
    target_set = set(target_ngrams)

    if len(source_set) == 0 or len(target_set) == 0:
        return 0

    intersection = source_set.intersection(target_set)

    similarity = len(intersection) / len(target_set)

    return similarity


class IComparsionAlgorithm(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def compare(self, user_text: str, db_text: str) -> float:
        pass


class NGramComparsionAlgorithm(IComparsionAlgorithm):
    def __init__(self):
        pass

    def compare(self, user_text: str, db_text: str) -> float:
        return jaccard_similarity(
            generate_n_grams(db_text, NGRAM_SIZE),
            generate_n_grams(user_text, NGRAM_SIZE),
        )


class TDIDFComparsionAlgorithm(IComparsionAlgorithm):
    def __init__(self):
        pass

    def compare(self, user_text: str, db_text: str) -> float:
        if db_text == "":
            return 0

        tfidf_matrix = TF_IDF_VECTORIZER.transform([user_text])
        tfidf_matrix_2 = TF_IDF_VECTORIZER.transform([db_text])

        tfidf_vectorbh = tfidf_matrix.toarray().flatten()
        tfidf_vectorbh_2 = tfidf_matrix_2.toarray().flatten()

        similarity_matrix = cosine_similarity(
            tfidf_vectorbh.reshape(1, -1), tfidf_vectorbh_2.reshape(1, -1)
        )

        return similarity_matrix[0][0]




class ComparsionAlgorithm(IComparsionAlgorithm):
    def __init__(self):
        self.tdidf = TDIDFComparsionAlgorithm()
        self.ngram = NGramComparsionAlgorithm()

    def compare(self, user_text: str, db_text: str) -> float:

        tdidf_result = self.tdidf.compare(user_text, db_text)
        ngram_result = self.ngram.compare(user_text, db_text)

        if ngram_result > 35:
            average_result = (tdidf_result + ngram_result) / 2
            return average_result

        return ngram_result
