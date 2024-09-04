import abc

import aiohttp
from api.algorithm.imports import *
from fake_headers import Headers

fake_headers = Headers()


class IDownloader(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def download(self, url: str) -> str:
        pass


class Downloader(IDownloader):
    def __init__(self):
        pass

    def download(self, url: str) -> str:
        headers = fake_headers.generate()
        try:
            response = requests.get(
                url, headers=headers, verify=False, timeout=5, stream=True
            )
            response.raise_for_status()
            content = b""
            for chunk in response.iter_content(chunk_size=1024):
                content += chunk
        except requests.RequestException as e:
            return None

        try:
            parsed = parser.from_buffer(content)
            if not parsed["content"]:
                print("No text found")
            return parsed["content"] or ""
        except Exception as e:
            return None
