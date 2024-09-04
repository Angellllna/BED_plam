import abc
import logging

from api.algorithm.downloaders import Downloader
from api.algorithm.extract_keywords import ExtractKeywords
from api.algorithm.imports import *

logger = logging.getLogger(__name__)


class IUrlSearch(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def search(self, user_text: str) -> list[str]:
        pass


def google_search(query, api_key=API_KEY, cse_id=CSE_ID, start=1, num_results=10):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num_results, start=start).execute()
    return res


def paginate_search(
    query, api_key=API_KEY, cse_id=CSE_ID, total_results=10, results_per_page=10
):
    all_results = []
    for start in range(1, total_results + 1, results_per_page):
        results = google_search(query, api_key, cse_id, start, results_per_page)
        all_results.extend(results.get("items", []))
    return all_results


def extract_titles_and_links(search_results):
    titles_and_links = []

    for item in search_results:
        title = item.get("title")
        link = item.get("link")
        titles_and_links.append(link)

    return titles_and_links


def merge_lists(*args):
    merged_list = []
    for lst in args:
        merged_list.extend(lst)
    return merged_list


class GoogleUrlSearch(IUrlSearch):
    def __init__(self, language: str):
        self._keywords_extractor = ExtractKeywords()
        self._language = language

    def search(self, user_text: str) -> list[str]:
        total_results = 10

        text_for_finde = self._keywords_extractor.extract_keywords(
            user_text, self._language
        )
        text_for_finde = text_for_finde.replace('"', "")

        paginated_general_results = paginate_search(
            f"-filetype:pdf -filetype:docx {text_for_finde}".strip(),
            total_results=total_results,
        )
        paginated_pdf_results = paginate_search(
            f"filetype:pdf {text_for_finde}".strip(), total_results=total_results
        )
        paginated_docx_results = paginate_search(
            f"filetype:docx {text_for_finde}".strip(), total_results=total_results
        )

        titles_and_links_general = extract_titles_and_links(paginated_general_results)
        titles_and_links_pdf = extract_titles_and_links(paginated_pdf_results)
        # titles_and_links_docx = extract_titles_and_links(paginated_docx_results)

        merged_list = merge_lists(titles_and_links_general, titles_and_links_pdf)

        return merged_list


class CustomVectorDatabaseUrlSearch(IUrlSearch):
    def exstract_urls(self, search_results: list[dict]) -> list[str]:
        urls_list = (
            [result["url"] for result in search_results["results"]]
            if "results" in search_results
            else []
        )
        return urls_list

    def search_custom_vector_database(
        self, token: str, user_text: str, results_count: int
    ) -> list[str]:
        url = f"https://search-api.94537961.xyz/search/?token={token}&query={user_text}&results_count={results_count}"
        search_results = requests.get(url).json()
        urls_list = self.exstract_urls(search_results)
        return urls_list

    def search(self, user_text: str) -> list[str]:
        total_results = 10

        search_results = self.search_custom_vector_database(
            CUSTOM_TOKEN_KEY, user_text, total_results
        )

        return search_results


class MergeSearches(IUrlSearch):
    def __init__(self, searches: list[IUrlSearch]):
        self._searches = searches

    def search(self, user_text: str) -> list[str]:
        results = merge_lists(*[search.search(user_text) for search in self._searches])

        return results

