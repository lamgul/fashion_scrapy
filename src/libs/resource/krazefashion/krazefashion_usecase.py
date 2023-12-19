from __future__ import annotations

import logging
from typing import List, Tuple, Literal

from src.config.context import Transactional
from src.libs.resource.abstracts.abstract_usecase import (
    AbstractUsecase,
    AbstractUsecaseCRUDImplements,
    AbstrctUsecaseCrawlerImplements

)
from src.libs.resource.common.universal_entity import UniversalEntity
from src.libs.resource.krazefashion.krazefashion_entity import KrazeFashionEntity
from src.libs.resource.krazefashion.krazefashion_service import KrazeFashionService
from src.libs.utils.content_creator import ContentCreator

KRAZFASHION_USECASE_LOGGER = logging.getLogger("uvicorn.error")


class KrazeFashionUsecase(
    AbstractUsecase,
    AbstractUsecaseCRUDImplements[UniversalEntity],
    AbstrctUsecaseCrawlerImplements
):

    def __init__(self):
        self.service = KrazeFashionService()
        self.content_creator = ContentCreator()

    @Transactional()
    def get_content_list(self,
                         sort_key: str = None,
                         sort_type: Literal['DESC', 'ASC'] = None,
                         page: int = None,
                         item_per_page: int = None
                         ) -> Tuple[List[UniversalEntity], int]:
        return self.krazefashion_repository.find_by(
            sort_key=sort_key,
            sort_type=sort_type,
            page=page,
            item_per_page=item_per_page
        )

    @Transactional()
    def get_content(self, trace_id: str):
        return self.krazefashion_repository.find_by_trace_id(trace_id=trace_id)

    @Transactional()
    def get_count(self) -> int:
        return self.krazefashion_repository.get_count()

    @Transactional()
    def daily_collect(self):
        fetched_urls = self.service.fetch_content_list()

        fetched_contents = [self.service.fetch_content(url) for url in fetched_urls]
        fetched_titles = []
        for fetched_content in fetched_contents:
            fetched_titles.append(fetched_content.title)

        saved_contents = self.krazefashion_repository.find_by_titles(titles=fetched_titles)
        saved_titles = [saved_content.title for saved_content in saved_contents]

        not_exsit_titles = self.service.not_exist_titles(fetched_titles=fetched_titles, saved_titles=saved_titles)

        for fetched_content in fetched_contents:
            if fetched_content.title in not_exsit_titles:
                self.krazefashion_repository.add(krazefashion_entity=KrazeFashionEntity.from_dto(fetched_content))

        self.service.update_notify(count=len(not_exsit_titles))

    def all_collect(self):
        fetched_urls = self.service.fetch_content_list()

        fetched_contents = [self.service.fetch_content(url) for url in fetched_urls]
        fetched_titles = []
        for fetched_content in fetched_contents:
            fetched_titles.append(fetched_content.title)
            self.service.logging(logger=KRAZFASHION_USECASE_LOGGER, data=fetched_content.reference_date)

        with self.session.begin():
            saved_contents = self.krazefashion_repository.find_by_titles(titles=fetched_titles)
            saved_titles = [saved_content.title for saved_content in saved_contents]

            not_exsit_titles = self.service.not_exist_titles(fetched_titles=fetched_titles, saved_titles=saved_titles)

            for fetched_content in fetched_contents:
                if fetched_content.title in not_exsit_titles:
                    self.krazefashion_repository.add(krazefashion_entity=KrazeFashionEntity.from_dto(fetched_content))

        self.service.update_notify(count=len(not_exsit_titles))
