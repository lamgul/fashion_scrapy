from __future__ import annotations

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilterAbstractScrapFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        return BeautifulSoup(self.html_source, "html.parser").find("main", {"id": "site-content"})


class SelectElementTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag):
        single_post = html_element.find("div", {"class": "main_section single_post"})
        row = single_post.find("div", {"class": "row"})
        return row


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        data = {
            'title': self._extract_title(html_element),
            'reference_date': self._extract_reference_date(html_element),
            'content': self._extract_content(html_element),
            'thumbnail': self._extract_thumbnail(html_element)
        }

        return data

    @staticmethod
    def _extract_title(content_tags: element.Tag) -> str:
        title_element = content_tags.find("h1")
        return title_element.text if title_element else ""

    @staticmethod
    def _extract_reference_date(content_tags: element.Tag) -> str:
        date_element = content_tags.find("p", {"class": "date_published"})
        return date_element.text if date_element else ""

    @staticmethod
    def _extract_content(content_tags: element.Tag) -> str:
        content = ''
        for content_tag in content_tags:
            if content_tag.text:
                content += content_tag.text
        return content

    @staticmethod
    def _extract_thumbnail(content_tags: element.Tag) -> str:
        for img in content_tags.find_all("div", {"class": "wp-block-image"}):
            thumbnail_element = img.find("img")
            if thumbnail_element and (thumbnail := thumbnail_element.get("data-lazy-src")):
                return thumbnail

        for img in content_tags.find_all('img'):
            if (thumbnail := img.get("data-lazy-src")):
                return thumbnail

        return ""
