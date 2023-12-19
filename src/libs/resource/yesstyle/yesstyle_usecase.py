from __future__ import annotations

import time
from random import uniform

from src.adapter import slack
from src.config.context import Transactional
from src.libs.resource.abstracts.abstract_usecase import (
    AbstractUsecase,
    AbstractUsecaseCRUDImplements,
    AbstrctUsecaseCrawlerImplements

)
from src.libs.resource.common.universal_entity import UniversalEntity
from src.libs.resource.yesstyle.yesstyle_service import YesstyleService


class YesstyleUsecase(AbstractUsecase, AbstractUsecaseCRUDImplements, AbstrctUsecaseCrawlerImplements):
    service = YesstyleService()

    @Transactional()
    def get_content_list(
            self,
            sort_key,
            sort_type,
            page,
            item_per_page
    ):
        return self.yesstyle_repository.find_by(
            sort_key=sort_key,
            sort_type=sort_type,
            page=page,
            item_per_page=item_per_page
        )

    @Transactional()
    def get_content(self, trace_id: str):
        return self.yesstyle_repository.find_by_trace_id(trace_id=trace_id)

    @Transactional()
    def get_count(self) -> int:
        return self.yesstyle_repository.get_count()

    @Transactional()
    def daily_collect(self):
        start_page = 1

        fetched_urls = self.service.fetch_content_list(page=start_page)
        fetched_contents = [self.service.fetch_content(url) for url in fetched_urls]
        fetched_contents_titles = [str(fetched_content.title) for fetched_content in fetched_contents]

        saved_contents = self.yesstyle_repository.find_by_titles(titles=fetched_contents_titles)
        saved_contents_titles = [saved_content.title for saved_content in saved_contents]

        not_exsit_content_titles = self.service.not_exist_content(
            fetched_contents_by_titles=fetched_contents_titles,
            saved_contents_by_titles=saved_contents_titles
        )

        if len(not_exsit_content_titles) == 0:
            slack.send_to_slack(data="[INFO] Yesstyle Update Missing")
            return

        for not_exsit_conent_title in not_exsit_content_titles:
            for fetched_content in fetched_contents:
                if not_exsit_conent_title == fetched_content.title:
                    self.yesstyle_repository.add(unversal_entity=UniversalEntity.new(
                        trace_id=fetched_content.trace_id,
                        reference_id=fetched_content.reference_id,
                        reference_date=self.service.to_datetime(fetched_content.reference_date),
                        reference_link=fetched_content.reference_link,
                        title=fetched_content.title,
                        content=fetched_content.content,
                        thumbnail=fetched_content.thumbnail
                    ))
        slack.send_to_slack(
            data=f"[INFO]Yesstyle Update After ...{len(not_exsit_content_titles)}"
        )

    @Transactional()
    def all_collect(self):
        statistics = {"count": 0}
        start_page = 1
        stop_collect = True

        while stop_collect:
            time.sleep(uniform(1.5, 2.5))
            fetched_urls = self.service.fetch_content_list(page=start_page)
            if not fetched_urls:
                slack.send_to_slack(data=f"[INFO] Yesstyle Collect ...{statistics['count']}")
                break

            for url in fetched_urls:
                fetched_content = self.service.fetch_content(url)
                if fetched_content is not None:
                    if self.service.is_stop_collect(self.service.to_datetime(fetched_content.reference_date)):
                        stop_collect = False
                        break

                    save_content = self.yesstyle_repository.find_by_title(title=fetched_content.title)
                    if save_content is None:
                        self.yesstyle_repository.add(unversal_entity=UniversalEntity.new(
                            trace_id=fetched_content.trace_id,
                            reference_id=fetched_content.reference_id,
                            reference_date=self.service.to_datetime(fetched_content.reference_date),
                            reference_link=fetched_content.reference_link,
                            title=fetched_content.title,
                            content=fetched_content.content,
                            thumbnail=fetched_content.thumbnail
                        ))
                        statistics['count'] += 1

            start_page += 1

