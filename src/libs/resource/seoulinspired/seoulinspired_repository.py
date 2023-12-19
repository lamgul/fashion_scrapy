from __future__ import annotations

import uuid
from typing import List, Optional, Literal, Any, Type

from sqlalchemy import func

from src.libs.resource.abstracts.abstract_repository import AbstractRepository
from src.libs.resource.common import define
from src.libs.resource.seoulinspired.seoulinspired_entity import SeoulInspiredEntity


class SeoulInspiredRepository(AbstractRepository):

    def add(self, seoulinspired_entity: SeoulInspiredEntity) -> SeoulInspiredEntity:
        self._session.add(seoulinspired_entity)
        self._session.flush()
        return seoulinspired_entity

    def update(self, seoulinspired_entity: SeoulInspiredEntity) -> SeoulInspiredEntity:
        self._session.query(SeoulInspiredEntity).filter(
            SeoulInspiredEntity.reference_id == seoulinspired_entity.reference_id
        ).update({
            SeoulInspiredEntity.reference_date: seoulinspired_entity.reference_date,
            SeoulInspiredEntity.reference_link: seoulinspired_entity.reference_link,
            SeoulInspiredEntity.thumbnail: seoulinspired_entity.thumbnail,
            SeoulInspiredEntity.title: seoulinspired_entity.title,
            SeoulInspiredEntity.content: seoulinspired_entity.content,
        })

        return seoulinspired_entity

    def update_by_convert(self, trace_id: uuid.UUID, is_convert: define.CONVERT):
        self._session.query(SeoulInspiredEntity).filter(
            SeoulInspiredEntity.trace_id == trace_id
        ).update({SeoulInspiredEntity.is_convert: is_convert})

    def find_by(
            self,
            page: int,
            item_per_page: int,
            sort_key: str,
            sort_type: Literal["DESC", "ASC"],
    ) -> tuple[List[SeoulInspiredEntity], Any]:
        query = self._session.query(SeoulInspiredEntity) \
            .order_by(sort_key, "id") \
            .limit(item_per_page) \
            .offset(self.get_page_limit(page, item_per_page))

        count_query = self._session.query(func.count(SeoulInspiredEntity.id))

        return query.all(), count_query.scalar()

    def find_by_trace_id(self, trace_id: str) -> SeoulInspiredEntity:
        query = self._session.query(SeoulInspiredEntity).filter(SeoulInspiredEntity.trace_id == trace_id)
        return query.one_or_none()

    def find_by_reference_id(self, reference_id: int) -> Optional[SeoulInspiredEntity]:
        query = self._session.query(SeoulInspiredEntity).where(SeoulInspiredEntity.reference_id == reference_id)
        return query.one_or_none()

    def find_by_reference_ids(self, reference_ids: list[int]) -> List[Type[SeoulInspiredEntity]]:
        query = self._session.query(SeoulInspiredEntity).where(SeoulInspiredEntity.reference_id.in_(reference_ids))
        return query.all()
