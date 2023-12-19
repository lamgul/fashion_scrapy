from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter

from typing import Optional


class InitContentTagFilterAbstractScrapFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        return BeautifulSoup(self.html_source, "html.parser")


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        return {
            "title": self._extract_title(html_element),
            "reference_id": self._extract_reference_id(html_element),
            "reference_date": self._extract_reference_date(html_element),
            "content": self._extract_content(html_element),
            "thumbnail": self._extract_thumbnail(html_element)
        }

    @staticmethod
    def _extract_title(html_element: element.Tag) -> str:
        title_element = html_element.find("h1", {"class": "entry-title"})
        return title_element.text.replace("\n", "")

    @staticmethod
    def _extract_reference_id(html_element: element.Tag) -> Optional[str]:
        article_element = html_element.find("article")
        return article_element.get("id").split("-")[1]

    @staticmethod
    def _extract_reference_date(html_element: element.Tag) -> Optional[str]:
        date_element = html_element.find("meta", {"property": "article:published_time"})
        return date_element.get("content").split("T")[0]

    @staticmethod
    def _extract_content(html_element: element.Tag) -> str:
        content_element = html_element.find("div", {"class": "entry-content"})
        return str(content_element) if content_element else ""

    @staticmethod
    def _extract_thumbnail(html_element: element.Tag) -> Optional[str]:
        content_element = html_element.find("div", {"class": "entry-content"})
        img_element = content_element.find("img") if content_element else None
        return img_element.get("data-src") if img_element else ""
