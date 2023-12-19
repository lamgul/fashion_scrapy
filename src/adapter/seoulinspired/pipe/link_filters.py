from bs4 import BeautifulSoup, element

from src.adapter.abstract.abstract_pipe import AbstractScrapFilter


class InitContentTagFilter(AbstractScrapFilter):

    def __init__(self, html_source: str):
        self.html_source = html_source

    def execute(self):
        soup = BeautifulSoup(self.html_source, "html.parser") \
            .find("div", {"class": "blog"})
        return soup


class ExtractContentLinkFilter(AbstractScrapFilter):

    def execute(self, html_element: element.Tag):
        links = []

        element_tag = html_element.findAll("div", {"class": "entry-main-header post-header"})
        for elem in element_tag:
            links.append(elem.find('a').get('href'))

        links = list(set(links))
        return links
