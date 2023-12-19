from __future__ import annotations

from typing import Dict

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        return BeautifulSoup(self.html_source, "html.parser")


class SelectElementTagFilter(AbstractScrapFilter):

    def execute(self, html_element):
        return html_element.find("div", {"class": "wp-site-blocks"})


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> Dict[str, str]:
        data = {
            "title": self._extract_title(html_element),
            "reference_date": self._extract_reference_date(html_element),
            "thumbnail": self._extract_thumbnail(html_element),
            "content": self._extract_content(html_element)
        }
        return data

    @staticmethod
    def _extract_title(html_element: element.Tag) -> str:
        title = ""
        for e in html_element:
            if isinstance(e, element.Tag):
                if found_title := e.find("h1", {
                    'style': 'margin-bottom: 0px; margin-top: 0px; margin-right: 0px; margin-left: 0px;',
                    'class': ['has-text-align-center', 'alignwide', 'ys-post-title', 'wp-block-post-title',
                              'has-source-serif-pro-font-family']}):
                    title = found_title.text
                    break
        return title

    @staticmethod
    def _extract_reference_date(html_element: element.Tag) -> str:
        reference_date = ""
        for e in html_element:
            if isinstance(e, element.Tag):
                if date_published := e.find("div", {"class": "wp-block-post-date"}):
                    reference_date = date_published.find("time")['datetime']
                    break
        return reference_date

    @staticmethod
    def _extract_thumbnail(html_element: element.Tag) -> str:
        thumbnail = ""
        for e in html_element:
            if isinstance(e, element.Tag):
                if found_thumbnail := e.find("figure", {
                    "class": ["ys-post-featured-image wp-block-post-featured-image"]}):
                    thumbnail = found_thumbnail.find("img")["src"]
                    break
        return thumbnail

    @staticmethod
    def _extract_content(html_element: element.Tag) -> str:
        content = ""
        for e in html_element:
            if isinstance(e, element.Tag):
                for each in e.findAll("div"):
                    if each.attrs.get("class", None) and "entry-content" in each.attrs.get("class", None):
                        content += each.text

                        if img := each.find("img"):
                            content += img['src']
        return content
