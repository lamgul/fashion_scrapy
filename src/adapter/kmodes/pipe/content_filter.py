from __future__ import annotations

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        soup = BeautifulSoup(self.html_source, "html.parser") \
            .find("div", {"class": "se-viewer se-theme-default"})
        return soup


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        data = {
            "title": self._extract_title(html_element),
            "reference_date": self._extract_reference_date(html_element),
            "thumbnail": self._extract_thumbnail(html_element),
            "content": self._extract_content(html_element)
        }
        return data

    @staticmethod
    def _extract_title(html_element) -> str:
        title_element = html_element.find("span", {"class": "se-fs- se-ff-"})
        return title_element.text

    @staticmethod
    def _extract_reference_date(html_element) -> str:
        date_element = html_element.find("span", {"class": "se_publishDate pcol2"})
        return date_element.text

    @staticmethod
    def _extract_thumbnail(html_element) -> str:
        img_element = html_element.find("img", {"class": "se-image-resource"})
        return img_element.get("data-lazy-src") or img_element.get("src") if img_element else ""

    @staticmethod
    def _extract_content(html_element) -> str:
        for tag in html_element.find_all("span", {"class": "__se-hash-tag"}):
            tag.decompose()
        p_tags = html_element.find_all("p", {"class": "se-text-paragraph"})
        return ''.join(i.text for i in p_tags if i.text != '\u200b')
