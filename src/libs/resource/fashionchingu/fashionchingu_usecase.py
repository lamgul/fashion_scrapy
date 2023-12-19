from __future__ import annotations

import logging
from typing import Optional, List

from src.adapter.fashionchingu.api.libs.dto import FashionChinguDto
from src.config.context import Transactional
from src.libs.resource.abstracts.abstract_usecase import (
    AbstractUsecase,
    AbstractUsecaseCRUDImplements,
    AbstrctUsecaseCrawlerImplements
)
from src.libs.resource.common.universal_entity import UniversalEntity
from src.libs.resource.fashionchingu.fashiochingu_entity import FashionChinguEntity
from src.libs.resource.fashionchingu.fashionchingu_service import FashionChinguService

FASHIONCHINGU_USECASE_LOGGER = logging.getLogger("uvicorn.error")


class FashionChinguUsecase(
    AbstractUsecase,
    AbstractUsecaseCRUDImplements[FashionChinguEntity],
    AbstrctUsecaseCrawlerImplements
):

    def __init__(self):
        self.service = FashionChinguService()

    @Transactional()
    def get_content_list(
            self,
            sort_key: str,
            sort_type: str,
            page: int,
            item_per_page: int
    ):
        return self.fashionchingu_repository.find_by(
            sort_key=sort_key,
            sort_type=sort_type,
            page=page,
            item_per_page=item_per_page
        )

    @Transactional()
    def get_content(self, trace_id: str) -> Optional[UniversalEntity]:
        return self.fashionchingu_repository.find_by_trace_id(trace_id=trace_id)

    @Transactional()
    def get_count(self):
        return self.fashionchingu_repository.get_count()

    def daily_collect(self):
        fetched_links = self.service.fetch_links(page=1)

        fetched_contents: List[FashionChinguDto] = []
        for link in fetched_links:
            fetched_content = self.service.fetch_content(link)
            fetched_contents.append(fetched_content)
            self.service.logging(logger=FASHIONCHINGU_USECASE_LOGGER, data=fetched_content.reference_date)

        with self.session.begin():
            saved_contents = self.fashionchingu_repository.find_by_titles(
                titles=[item.title for item in fetched_contents]
            )

            not_exist_contents_by_titles = self.service.not_exist_contents(
                fetched_content_titles=[fetched_content.title for fetched_content in fetched_contents],
                save_content_titles=[saved_content.title for saved_content in saved_contents]
            )

            for not_exist_content_title in not_exist_contents_by_titles:
                for fetched_content in fetched_contents:
                    if not_exist_content_title == fetched_content.title:
                        self.fashionchingu_repository.add(
                            fashionchingu_entity=FashionChinguEntity.from_dto(fetched_content)
                        )

        self.service.update_notify(count=len(not_exist_contents_by_titles))

    def all_collect(self):
        start_page = 1
        statistics = {"count": 0}

        fashionchingu_dtos = []
        while True:
            links = self.service.fetch_links(page=start_page)
            if links is None:
                break
            for link in links:
                fashionchingu_dto = self.service.fetch_content(link)
                self.service.logging(logger=FASHIONCHINGU_USECASE_LOGGER, data=fashionchingu_dto.reference_date)
                fashionchingu_dtos.append(fashionchingu_dto)

            start_page += 1

        with self.session.begin():
            for fashionchingu_dto in fashionchingu_dtos:
                fashionchingu_entity = self.fashionchingu_repository.find_by_title(title=fashionchingu_dto.title)
                if fashionchingu_entity is None:
                    self.fashionchingu_repository.add(
                        fashionchingu_entity=FashionChinguEntity.from_dto(fashionchingu_dto=fashionchingu_dto)
                    )
                    statistics['count'] += 1
                else:
                    self.fashionchingu_repository.update(
                        fashionchingu_entity=FashionChinguEntity.from_dto(fashionchingu_dto=fashionchingu_dto)
                    )

        self.service.update_notify(count=statistics['count'])
