import uuid
from typing import Optional, List

import backoff
import fake_useragent
import requests

from src.adapter.seoulinspired.api.libs.dto import SeoulInspiredDto
from src.adapter.seoulinspired.pipe import link_filters, content_filters
from src.adapter.seoulinspired.pipe.pipes import SeoulInspiredPipeLine, SeoulInspiredScrapPipeLine
from src.adapter.utils import ByPassRequestMixin


class SeoulInspiredApi(ByPassRequestMixin):
    HOST = "https://www.seoulinspired.com"
    UserAgent = fake_useragent.UserAgent().random

    @backoff.on_exception(backoff.expo, requests.exceptions.ReadTimeout, max_tries=5)
    def get_links(self, page: int) -> Optional[List[str]]:
        _endpoint = f"/lifestyle/fashion/page/{page}/"

        resp = self.request.get(
            url=self.HOST + _endpoint,
            headers={"User-Agent": self.UserAgent},
        )
        if resp.status_code == 200:
            pipeline = SeoulInspiredPipeLine(init_filter=link_filters.InitContentTagFilter(html_source=resp.text))
            pipeline.append_filter(link_filters.ExtractContentLinkFilter())
            pipeline.start()

            return pipeline.get_data()

    def emit(self, url: str) -> SeoulInspiredDto:
        resp = self.request.get(url=url, timeout=3)
        if resp.status_code == 200:
            pipline = SeoulInspiredScrapPipeLine(
                init_filter=content_filters.InitContentTagFilterAbstractScrapFilter(html_source=resp.text)
            )
            pipline.append_filter(content_filters.ExtractContentTagFilter())
            pipline.start()
            data = pipline.get_dict()

            return SeoulInspiredDto.new(
                trace_id=uuid.uuid4(),
                reference_id=data['reference_id'],
                reference_date=data['reference_date'],
                reference_link=url,
                title=data['title'],
                content=data['content'],
                thumbnail=data['thumbnail']
            )
