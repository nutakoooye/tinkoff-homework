from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class HeaderParserInterface(ABC):
    @abstractmethod
    def parse_header(self, page: str) -> str:
        pass


class YoutubeHeaderParser(HeaderParserInterface):
    def parse_header(self, page: str) -> str:
        soup = BeautifulSoup(page, "html.parser")
        title = soup.title.text
        title = title.replace(" - YouTube", "")
        return title.strip()


class YMusicHeaderParser(HeaderParserInterface):
    def parse_header(self, page: str) -> str:
        soup = BeautifulSoup(page, "html.parser")
        try:
            data = (
                soup.find("div", class_="sidebar__section")
                .find("div", class_="sidebar-track__title")
                .find("a")
            )
            return data.text.strip()
        except AttributeError:
            return "Not found header"


class HabrHeaderParser(HeaderParserInterface):
    def parse_header(self, page: str) -> str:
        soup = BeautifulSoup(page, "html.parser")
        try:
            data = soup.find("h1", class_="tm-article-snippet__title").find(
                "span"
            )
            return data.text.strip()
        except AttributeError:
            return "Not found header"


class Context:
    def __init__(self, parser: HeaderParserInterface):
        self.__parser: HeaderParserInterface = parser

    def parse_header(self, url: str) -> str:
        response = requests.get(url)
        return self.__parser.parse_header(response.text)
