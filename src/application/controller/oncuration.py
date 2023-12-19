from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse

from src.application.controller.type_define import USECASE_TYPE
from src.libs.resource.oncuration.oncuration_usecase import OncurationUsecase

oncuration_router = APIRouter(tags=['Oncuration'], prefix="/api")


@oncuration_router.get(path="/oncuration")
def oncuration_list(
        sort_key: Literal['id', 'reference_date'] = Query(default='id'),
        sort_type: Literal['DESC', 'ASC'] = Query(default='DESC'),
        page: int = Query(default=1),
        item_per_page: int = Query(default=10),

        usecase: USECASE_TYPE = Depends(OncurationUsecase)
):
    oncuration_contents_list, oncuration_contents_count = usecase.get_content_list(
        page=page,
        item_per_page=item_per_page,
        sort_key=sort_key,
        sort_type=sort_type
    )

    return JSONResponse(status_code=200, content={
        "page": page,
        "item_per_page": item_per_page,
        "total_count": oncuration_contents_count,
        "items": [{
            "trace_id": oncuration.trace_id,
            "reference_id": oncuration.reference_id,
            "reference_date": str(oncuration.reference_date),
            "reference_link": oncuration.reference_link,
            "thumbnail": oncuration.thumbnail,
            "is_convert": oncuration.is_convert,
            "title": str(oncuration.title)
        } for oncuration in oncuration_contents_list]})


@oncuration_router.get(path="/oncuration/{trace_id:str}")
def oncuration_retreieve(
        trace_id: str = Path(),
        usecase: USECASE_TYPE = Depends(OncurationUsecase)
):
    oncuration = usecase.get_content(trace_id=trace_id)
    if oncuration is None:
        return JSONResponse(status_code=404, content={})

    return JSONResponse(status_code=200, content={
        "trace_id": oncuration.trace_id,
        "reference_id": oncuration.reference_id,
        "reference_date": oncuration.reference_date.isoformat(),
        "reference_link": oncuration.reference_link,
        "thumbnail": oncuration.thumbnail,
        "is_convert": oncuration.is_convert,
        "title": oncuration.title,
        "content": oncuration.content
    })


@oncuration_router.post(path="/oncuration/{trace_id:str}/convert")
def oncuration_convert(
        trace_id: str = Path(),
        usecase: USECASE_TYPE = Depends(OncurationUsecase)
):
    return JSONResponse(status_code=200, content=usecase.convert(trace_id=trace_id))
