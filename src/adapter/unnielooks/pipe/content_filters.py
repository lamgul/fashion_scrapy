import json

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilterAbstractScrapFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        return BeautifulSoup(self.html_source, "html.parser")


class ExtractContentTagFilter(AbstractScrapFilter):
    _FILTER_LENGTH = 500

    def execute(self, html_element: element.Tag):
        data = {
            "title": html_element.find('h1', {"class": "article-template__title"}).text,
            "content": [],
            "reference_id": None,
            "reference_date": "",
            "thumbnail": "",

        }

        contents = html_element.find("div", {"class": "article-template__content"})
        for content in contents:
            if img := content.find("a"):
                if isinstance(img, element.Tag):
                    data['content'].append(img.get("href"))
            else:
                data['content'].append(content.text)

        thumbnail_element = html_element.find("div", {"class": "article-template__hero-medium media"})

        data["thumbnail"] = 'https:' + thumbnail_element.find("img").get('src') if thumbnail_element else ""

        meta_datas = html_element.find_all("script", {"class": "ws_schema"})
        for meta_data in meta_datas:
            if len(meta_data.text) > self._FILTER_LENGTH:
                json_content = json.loads(meta_data.text)
                data['reference_date'] = json_content['datePublished']

        return data


class ExtractContentTagFilter(AbstractScrapFilter):
    _FILTER_LENGTH = 500

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        data = {
            "title": self._extract_title(html_element),
            "content": self._extract_content(html_element),
            "reference_date": self._extract_reference_date(html_element, self._FILTER_LENGTH),
            "thumbnail": self._extract_thumbnail(html_element),
        }

        return data

    @staticmethod
    def _extract_title(html_element: element.Tag) -> str:
        return html_element.find('h1', {"class": "article-template__title"}).text

    @staticmethod
    def _extract_content(html_element: element.Tag) -> str:
        contents = html_element.find("div", {"class": "article-template__content"})
        content_list = []
        for content in contents:
            if img := content.find("a"):
                if isinstance(img, element.Tag):
                    content_list.append(img.get("href"))
            else:
                content_list.append(content.text)
        return '\n'.join(filter(None, content_list))

    @staticmethod
    def _extract_thumbnail(html_element: element.Tag) -> str:
        thumbnail_element = html_element.find("div", {"class": "article-template__hero-medium media"})
        return 'https:' + thumbnail_element.find("img").get('src') if thumbnail_element else ""

    @staticmethod
    def _extract_reference_date(html_element: element.Tag, filter_length: int) -> str:
        meta_datas = html_element.find_all("script", {"class": "ws_schema"})
        for meta_data in meta_datas:
            if len(meta_data.text) > filter_length:
                json_content = json.loads(meta_data.text)
                return json_content['datePublished']
        return ""
