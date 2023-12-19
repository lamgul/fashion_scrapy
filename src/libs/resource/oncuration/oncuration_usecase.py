from __future__ import annotations

import logging
from typing import List, Optional, Tuple, Literal

from src.adapter.oncuration.api.libs.dto import OncurationDto
from src.config.context import Transactional
from src.libs.resource.abstracts.abstract_usecase import (
    AbstractUsecase,
    AbstractUsecaseCRUDImplements,
    AbstrctUsecaseCrawlerImplements

)
from src.libs.resource.common.universal_entity import UniversalEntity
from src.libs.resource.oncuration.oncuration_entity import OncurationEntity
from src.libs.resource.oncuration.oncuration_service import OncurationService
from src.libs.utils.content_creator import ContentCreator

ONCURATION_USECASE_LOGGER = logging.getLogger("uvicorn.error")


class OncurationUsecase(
    AbstractUsecase,
    AbstractUsecaseCRUDImplements[UniversalEntity],
    AbstrctUsecaseCrawlerImplements
):

    def __init__(self):
        self.service = OncurationService()
        self.content_creator = ContentCreator()

    @Transactional()
    def get_content_list(self,
                         sort_key: str = None,
                         sort_type: Literal['DESC', 'ASC'] = None,
                         page: int = None,
                         item_per_page: int = None
                         ) -> Tuple[List[UniversalEntity], int]:
        return self.oncuration_repository.find_by(
            sort_key=sort_key,
            sort_type=sort_type,
            page=page,
            item_per_page=item_per_page
        )

    @Transactional()
    def get_content(self, trace_id: str) -> Optional[OncurationEntity]:
        return self.oncuration_repository.find_by_trace_id(trace_id=trace_id)

    @Transactional()
    def get_count(self) -> int:
        return self.oncuration_repository.get_count()

    @Transactional()
    def daily_collect(self):
        start_page = 1

        fetched_urls = self.service.fetch_content_list(page=start_page)
        fetched_contents = [self.service.fetch_content(url) for url in fetched_urls]
        fetched_reference_ids = [fetched_content.reference_id for fetched_content in fetched_contents]

        saved_contents = self.oncuration_repository.find_by_reference_ids(reference_ids=fetched_reference_ids)
        saved_reference_ids = [saved_content.reference_id for saved_content in saved_contents]

        not_exsit_reference_ids = self.service.not_exist_reference_ids(
            fetched_reference_ids=fetched_reference_ids,
            saved_reference_ids=saved_reference_ids
        )
        for not_exsit_reference_id in not_exsit_reference_ids:
            for fetched_content in fetched_contents:
                if not_exsit_reference_id == fetched_content.reference_id:
                    self.oncuration_repository.add(
                        oncuration_entity=OncurationEntity.from_dto(fetched_content))

        self.service.update_notify(count=len(not_exsit_reference_ids))


    def all_collect(self):
        oncuration_dtos: List[OncurationDto] = []
        fetched_reference_ids = []
        start_page = 1
        stop_collect = True

        while stop_collect:
            fetch_content_list = self.service.fetch_content_list(page=start_page)

            for link in fetch_content_list:
                fetched_content = self.service.fetch_content(link)

                if self.service.is_stop_collect(self.service.to_datetime(fetched_content.reference_date)):
                    stop_collect = False
                    break

                oncuration_dtos.append(fetched_content)
                fetched_reference_ids.append(fetched_content.reference_id)

                self.service.logging(logger=ONCURATION_USECASE_LOGGER, data=fetched_content.reference_date)

            start_page += 1

        with self.session.begin():
            saved_contents = self.oncuration_repository.find_by_reference_ids(reference_ids=fetched_reference_ids)
            saved_reference_ids = [saved_content.reference_id for saved_content in saved_contents]

            not_exsit_reference_ids = self.service.not_exist_reference_ids(
                fetched_reference_ids=fetched_reference_ids,
                saved_reference_ids=saved_reference_ids
            )

            for oncuration_dto in oncuration_dtos:
                if oncuration_dto.reference_id in not_exsit_reference_ids:
                    self.oncuration_repository.add(
                        oncuration_entity=OncurationEntity.from_dto(oncuration_dto=oncuration_dto))
                else:
                    self.oncuration_repository.update(
                        oncuration_entity=OncurationEntity.from_dto(oncuration_dto=oncuration_dto))

        self.service.update_notify(count=len(oncuration_dtos))
