from __future__ import annotations

import logging
from typing import List, Optional, Tuple, Literal

from src.adapter.seoulinspired.api.libs.dto import SeoulInspiredDto
from src.config.context import Transactional
from src.libs.resource.abstracts.abstract_usecase import (
    AbstrctUsecaseCrawlerImplements,
    AbstractUsecaseCRUDImplements,
    AbstractUsecase
)
from src.libs.resource.common.universal_entity import UniversalEntity
from src.libs.resource.seoulinspired.seoulinspired_entity import SeoulInspiredEntity
from src.libs.resource.seoulinspired.seoulinspired_service import SeoulInspiredService
from src.libs.utils.content_creator import ContentCreator

SEOULINSPIRED_USECASE_LOGGER = logging.getLogger("uvicorn.error")


class SeoulInspiredUsecase(
    AbstractUsecase,
    AbstractUsecaseCRUDImplements,
    AbstrctUsecaseCrawlerImplements
):

    def __init__(self):
        self.service = SeoulInspiredService()
        self.content_creator = ContentCreator()

    @Transactional()
    def get_content_list(self,
                         sort_key: str = None,
                         sort_type: Literal['DESC', 'ASC'] = None,
                         page: int = None,
                         item_per_page: int = None
                         ) -> Tuple[List[UniversalEntity], int]:
        return self.seoulinspired_repository.find_by(
            sort_key=sort_key,
            sort_type=sort_type,
            page=page,
            item_per_page=item_per_page
        )

    @Transactional()
    def get_content(self, trace_id: str) -> Optional[SeoulInspiredEntity]:
        return self.seoulinspired_repository.find_by_trace_id(trace_id)

    @Transactional()
    def get_count(self):
        return self.seoulinspired_repository.get_count()

    @Transactional()
    def daily_collect(self):
        start_page = 1

        fetched_urls = self.service.fetch_links(page=start_page)
        fetched_contents = [self.service.fetch_content(url) for url in fetched_urls]
        fetched_reference_ids = [int(fetched_content.reference_id) for fetched_content in fetched_contents]

        saved_contents = self.seoulinspired_repository.find_by_reference_ids(reference_ids=fetched_reference_ids)
        saved_reference_ids = [int(saved_content.reference_id) for saved_content in saved_contents]

        not_exsit_reference_ids = self.service.not_exist_reference_ids(
            fetched_reference_ids=fetched_reference_ids,
            saved_reference_ids=saved_reference_ids
        )

        for not_exsit_reference_id in not_exsit_reference_ids:
            for fetched_content in fetched_contents:
                if not_exsit_reference_id == int(fetched_content.reference_id):
                    self.seoulinspired_repository.add(
                        seoulinspired_entity=SeoulInspiredEntity.from_dto(seoulinspired_dto=fetched_content))

        self.service.update_notify(count=len(not_exsit_reference_ids))

    def all_collect(self):
        seoulinspired_dtos: List[SeoulInspiredDto] = []
        fetched_reference_ids = []
        start_page = 1
        stop_collect = True

        while stop_collect:
            fetched_content_links = self.service.fetch_links(page=start_page)

            if len(fetched_content_links) != 12:
                stop_collect = False

            for link in fetched_content_links:
                fetched_content = self.service.fetch_content(link)
                fetched_reference_date = self.service.to_datetime(reference_date=fetched_content.reference_date)

                if self.service.is_reference_date_matching(reference_date=fetched_reference_date):
                    seoulinspired_dtos.append(fetched_content)
                    fetched_reference_ids.append(fetched_content.reference_id)

                    self.service.logging(logger=SEOULINSPIRED_USECASE_LOGGER, data=fetched_content.reference_date)

            start_page += 1

        with self.session.begin():
            saved_contents = self.seoulinspired_repository.find_by_reference_ids(reference_ids=fetched_reference_ids)
            saved_reference_ids = [int(saved_content.reference_id) for saved_content in saved_contents]

            not_exsit_reference_ids = self.service.not_exist_reference_ids(
                fetched_reference_ids=fetched_reference_ids,
                saved_reference_ids=saved_reference_ids
            )

            for seoulinspired_dto in seoulinspired_dtos:
                if seoulinspired_dto.reference_id in not_exsit_reference_ids:
                    self.seoulinspired_repository.add(
                        seoulinspired_entity=SeoulInspiredEntity.from_dto(seoulinspired_dto=seoulinspired_dto))
                else:
                    self.seoulinspired_repository.update(
                        seoulinspired_entity=SeoulInspiredEntity.from_dto(seoulinspired_dto=seoulinspired_dto))

        self.service.update_notify(count=len(seoulinspired_dtos))
