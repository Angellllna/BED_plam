import abc

from api.algorithm.imports import *


class ITextProcessor(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def preprocess_text(self, text: str) -> list[str]:
        pass


class TextUAProcessor(ITextProcessor):
    def __init__(self):
        self.tokenize_re = re.compile(r"\b\w+\b")
        self.nlp_uk = spacy.load("uk_core_news_sm")
        self.stop_words_uk = self.load_stop_words(
            "api/algorithm/stop_words_ukrainian.json"
        )

    def load_stop_words(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return set(json.load(file))
        except FileNotFoundError:
            logging.error(f"Error: The file {filepath} was not found.")
            return set()

    def preprocess_text(self, text):
        tokens = [match.lower() for match in self.tokenize_re.findall(text)]

        doc = self.nlp_uk(" ".join(tokens))
        return " ".join(
            [
                token.lemma_
                for token in doc
                if token.text.lower() not in self.stop_words_uk and not token.is_punct
            ]
        )


class TextENProcessor(ITextProcessor):
    def __init__(self):
        self.tokenize_re = re.compile(r"\b\w+\b")
        self.english_stop_words = set(stopwords.words("english"))
        self.nlp_en = spacy.load("en_core_web_sm")

    def preprocess_text(self, text):
        tokens = [match.lower() for match in self.tokenize_re.findall(text)]

        tokens = [token for token in tokens if token not in self.english_stop_words]

        doc = self.nlp_en(" ".join(tokens))

        return " ".join(
            [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        )
