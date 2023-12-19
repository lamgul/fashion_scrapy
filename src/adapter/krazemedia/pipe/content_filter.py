from __future__ import annotations

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        soup = BeautifulSoup(self.html_source, "html.parser") \
            .find("section", {"class": "Main-content"})
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
        title_element = html_element.find("h1", {"class": "BlogItem-title"})
        return title_element.text if title_element else ""

    @staticmethod
    def _extract_reference_date(html_element) -> str:
        date_element = html_element.find("time", {"class": "Blog-meta-item Blog-meta-item--date"}, datetime=True)
        return date_element.get("datetime") if date_element else ""

    @staticmethod
    def _extract_thumbnail(html_element) -> str:
        thumbnail_tag = html_element.find("div", {"class": "image-block-wrapper"})
        img = thumbnail_tag.find("img") if thumbnail_tag else None
        return img.get("data-src") if img else ""

    @staticmethod
    def _extract_content(html_element) -> str:
        content_list = []
        contents = html_element.find_all("div", {"class": "sqs-block-content"})
        for content_block in contents:
            if content_block.find("div", {"class": "sqs-html-content"}):
                p_tags = content_block.find_all('p', {"style": "white-space:pre-wrap;"})
                for p in p_tags:
                    content_list.append(p.text)

            if content_block.find("div", {"class": "image-block-wrapper"}):
                img_tag = content_block.find('img')
                if img_tag:
                    content_list.append(img_tag.get("data-src"))

            if content_block.find("blockquote"):
                sns_links = [a_tag.get('href') for a_tag in content_block.find_all('a') if a_tag.get('href')]
                if sns_links:
                    content_list.append(sns_links[-1])

        return "\n".join(content_list)
