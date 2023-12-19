from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter

STOP_DATE = "2022"


class RaiseStopException(Exception):
    """ 2022년 데이터면 종료 """


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        soup = BeautifulSoup(self.html_source, "html.parser") \
            .find("div", {"class": "detail_wrap"})
        return soup


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        data = {
            "title": self._extract_title(html_element=html_element),
            "content": self._extract_content(html_element=html_element),
            "reference_date": self._extract_reference_date(html_element=html_element),
            "thumbnail": self._extract_thumbnail(html_element=html_element)
        }

        if data["reference_date"].split("-")[0] == STOP_DATE:
            raise RaiseStopException()

        return data

    @staticmethod
    def _extract_title(html_element: element.Tag) -> str:
        title_element = html_element.find("h3", {"class": "d_title"})
        return title_element.text if title_element else ""

    @staticmethod
    def _extract_reference_date(html_element: element.Tag) -> str:
        date_element = html_element.find("p", {"class": "d_write"})
        return date_element.text.split("\xa0")[0] if date_element else ""

    @staticmethod
    def _extract_content(html_element: element.Tag) -> str:
        images: List[str] = [elem["src"] for elem in html_element.find_all("img")]
        content_element = html_element.find("div", {"class": "d_cont"})
        content = str(content_element) + '\n'.join(images) if content_element else ""
        return content

    @staticmethod
    def _extract_thumbnail(html_element: element.Tag) -> str:
        thumbnail: List[str] = [elem["src"] for elem in html_element.find_all("img")]
        return thumbnail[0] if thumbnail else ""
