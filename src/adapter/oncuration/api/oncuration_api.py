from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlparse, unquote

import requests

from src.adapter.oncuration.api.libs.dto import OncurationDto
from src.adapter.oncuration.pipe import content_filter, content_list_filter
from src.adapter.oncuration.pipe import pipes


class OncurationApi:
    HOST = "https://oncuration.com"

    def get_content_list(self, page: int) -> Optional[List[str]]:
        _endpoint = f"/fashion/page/{page}/"

        r = requests.get(self.HOST + _endpoint)
        if r.status_code == 200:
            pipeline = pipes.OncurationScrapPipeLine(
                init_filter=content_list_filter.InitContentTagFilter(html_source=r.text))
            pipeline.append_filter(content_list_filter.ExtractContentTagFilter())

            pipeline.start()

            return pipeline.get_result()
        else:
            return []

    def get_fashion_content(self, url: str) -> OncurationDto:
        r = requests.get(url)

        if r.status_code == 200:
            pipeline = pipes.OncurationScrapPipeLine(init_filter=content_filter.InitContentTagFilter(
                html_source=r.text))
            pipeline.append_filter(content_filter.ExtractContentTagFilter())

            pipeline.start()

            data = pipeline.get_data()

            return OncurationDto.new(
                reference_id=self._parse_url_path(url),
                reference_date=data['reference_date'],
                reference_link=url,
                title=data['title'],
                content=data['content'],
                thumbnail=data['thumbnail']
            )

    @staticmethod
    def _parse_url_path(url: str) -> str:
        parsed_url = urlparse(url)
        path = parsed_url.path
        last_segment = path.split('/')[1]

        return unquote(last_segment)
