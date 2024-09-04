import abc
import time

from api.algorithm.comparsion_algo import (
    ComparsionAlgorithm,
    IComparsionAlgorithm,
    NGramComparsionAlgorithm,
)
from api.algorithm.constants import POOL_SIZE
from api.algorithm.downloaders import Downloader
from api.algorithm.imports import *
from api.algorithm.search import (
    CustomVectorDatabaseUrlSearch,
    GoogleUrlSearch,
    IUrlSearch,
    MergeSearches,
)
from api.algorithm.text_preprocessors import (
    ITextProcessor,
    TextENProcessor,
    TextUAProcessor,
)


class IProcessingPipeline(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def process(self, user_text: str) -> str:
        pass


class ProcessingPipelineTemplate(IProcessingPipeline):
    def __init__(
        self,
        text_processor: ITextProcessor,
        url_search: IUrlSearch,
        compare: IComparsionAlgorithm,
    ):
        self._text_processor = text_processor
        self._url_search = url_search
        self._compare = compare
        self._downloader = Downloader()

    def process(self, user_text: str) -> list[tuple[str, float]]:
        start = time.time()
        preprocessed_text = self._text_processor.preprocess_text(user_text)
        # print(f"Preprocessing time: {time.time() - start:.2f}s")
        logging.info(f"Preprocessing time: {time.time() - start:.2f}s")
        start = time.time()

        links = self._url_search.search(user_text)
        # print(f"Search time: {time.time() - start:.2f}s")
        logging.info(f"Links: {links}")
        start = time.time()
        # print("Links: ", links)
        logging.info(f"Links: {links}")

        with Pool(4 * POOL_SIZE) as pool:
            texts_to_compare = pool.map(self._downloader.download, links)
            # print(f"Downloading time: {time.time() - start:.2f}s")
            logging.info(f"Downloading time: {time.time() - start:.2f}s")
            start = time.time()

        with Pool(POOL_SIZE) as pool:
            # print(f"Total links: {len(links)}")
            logging.info(f"Total links: {len(links)}")
            new_links = []
            new_texts_to_compare = []
            for index, text in enumerate(texts_to_compare):
                if text is not None:
                    new_links.append(links[index])
                    new_texts_to_compare.append(text)
            links = new_links
            texts_to_compare = new_texts_to_compare

            # print(f"Filtering time: {time.time() - start:.2f}s")
            logging.info(f"Filtering time: {time.time() - start:.2f}s")
            start = time.time()
            # print(f"Total links: {len(links)}")
            logging.info(f"Total links: {len(links)}")

            texts_to_compare = pool.map(
                self._text_processor.preprocess_text, texts_to_compare
            )
            print(f"Preprocessing time: {time.time() - start:.2f}s")
            start = time.time()

            results = pool.starmap(
                self._compare.compare,
                [(preprocessed_text, text) for text in texts_to_compare],
            )
            print(f"Comparing time: {time.time() - start:.2f}s")

        return list(zip(links, results))


class ProcessingPipeline(IProcessingPipeline):
    def __init__(self):
        self._language_to_pipeline: dict[str, ProcessingPipelineTemplate] = {
            "uk": ProcessingPipelineTemplate(
                TextUAProcessor(),
                GoogleUrlSearch(language="uk"),
                NGramComparsionAlgorithm(),
            ),
            "en": ProcessingPipelineTemplate(
                TextENProcessor(),
                MergeSearches(
                    [GoogleUrlSearch(language="en")
                     , CustomVectorDatabaseUrlSearch()
                     ]
                ),
                ComparsionAlgorithm(),
            ),
        }

    def process(self, user_text: str) -> list[tuple[str, float]]:
        detected_language = language.from_buffer(user_text)

        if not detected_language in self._language_to_pipeline:
            detected_language = "en"

        return self._language_to_pipeline[detected_language].process(user_text)
