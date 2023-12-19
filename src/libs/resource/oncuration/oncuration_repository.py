from __future__ import annotations

import uuid
from typing import List, Optional, Literal, Any, Type

from sqlalchemy import func

from src.libs.resource.abstracts.abstract_repository import AbstractRepository
from src.libs.resource.common import define
from src.libs.resource.oncuration.oncuration_entity import OncurationEntity


class OncurationRepository(AbstractRepository):

    def add(self, oncuration_entity: OncurationEntity) -> OncurationEntity:
        self._session.add(oncuration_entity)
        self._session.flush()
        return oncuration_entity

    def update(self, oncuration_entity: OncurationEntity) -> OncurationEntity:
        self._session.query(OncurationEntity).filter(
            OncurationEntity.reference_id == oncuration_entity.reference_id
        ).update({
            OncurationEntity.reference_date: oncuration_entity.reference_date,
            OncurationEntity.reference_link: oncuration_entity.reference_link,
            OncurationEntity.thumbnail: oncuration_entity.thumbnail,
            OncurationEntity.title: oncuration_entity.title,
            OncurationEntity.content: oncuration_entity.content,
        })

        return oncuration_entity

    def update_by_convert(self, trace_id: uuid.UUID, is_convert: define.CONVERT):
        self._session.query(OncurationEntity).filter(
            OncurationEntity.trace_id == trace_id
        ).update({OncurationEntity.is_convert: is_convert})

    def find_by(
            self,
            page: int,
            item_per_page: int,
            sort_key: str,
            sort_type: Literal["DESC", "ASC"],
    ) -> tuple[List[OncurationEntity], Any]:
        query = self._session.query(OncurationEntity) \
            .order_by(sort_key, "id") \
            .limit(item_per_page) \
            .offset(self.get_page_limit(page, item_per_page))

        count_query = self._session.query(func.count(OncurationEntity.id))

        return query.all(), count_query.scalar()

    def find_by_trace_id(self, trace_id: str) -> OncurationEntity:
        query = self._session.query(OncurationEntity).filter(OncurationEntity.trace_id == trace_id)
        return query.one_or_none()

    def find_by_reference_id(self, reference_id: str) -> Optional[OncurationEntity]:
        query = self._session.query(OncurationEntity).where(OncurationEntity.reference_id == reference_id)
        return query.one_or_none()

    def find_by_reference_ids(self, reference_ids: list[str]) -> List[Type[OncurationEntity]]:
        query = self._session.query(OncurationEntity).where(OncurationEntity.reference_id.in_(reference_ids))
        return query.all()
