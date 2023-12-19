from __future__ import annotations

from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source):
        self.html_source = html_source

    def execute(self):
        soup = BeautifulSoup(self.html_source, "html.parser")
        return soup


class ExtractContentTagFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag) -> dict[str, str]:
        data = {
            "title": self.extract_title(html_element),
            "reference_date": self.extract_reference_date(html_element),
            "content": self.extract_content(html_element),
            "thumbnail": self.extract_thumbnail(html_element)
        }
        return data

    @staticmethod
    def extract_title(html_element: element.Tag) -> str:
        parent = html_element.find("div", {"class": "infoArea"})
        return parent.find("h3", {"class": "title"}).text.strip()

    @staticmethod
    def extract_reference_date(html_element: element.Tag) -> str:
        parent = html_element.find("div", {"class": "infoArea"})
        return parent.find("span", {"class": "date"}).text.strip()

    @staticmethod
    def extract_content(html_element: element.Tag) -> str:
        contents_area = html_element.find("div", {"class": "contentsArea"})

        content_list = []
        for child in contents_area.children:
            content = None

            if child.name in ["h3", "p"]:
                content = child.text.strip()
            elif child.name == "figure":
                content = child.find("img").get("src", "")
            elif child.name == "div" and "wp-block-eedee-block-gutenslider" in child.get('class', []):
                content = "\n".join(img.get("src") for img in child.find_all("img") if img.get("src"))

            if content:
                content_list.append(content)

        return "\n".join(content_list)

    @staticmethod
    def extract_thumbnail(html_element: element.Tag) -> str:
        thumbnail_element = html_element.find("figure", {"class": "wp-block-image size-full"})
        if thumbnail_element:
            return thumbnail_element.find("img").get("src", "")

        slider_thumbnail = html_element.find("div", {"class": "wp-block-eedee-block-gutenslider"})
        if slider_thumbnail:
            return slider_thumbnail.find("img").get("src", "")

        return ""
