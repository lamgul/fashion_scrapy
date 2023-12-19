from typing import Literal

from fastapi import APIRouter, Path, Query, Depends
from fastapi.responses import JSONResponse

from src.application.controller.type_define import USECASE_TYPE
from src.libs.resource.seoulinspired.seoulinspired_usecase import SeoulInspiredUsecase

seoulinspired_router = APIRouter(tags=['Seoulinspired'], prefix="/api")


@seoulinspired_router.get(path="/seoulinspired")
def seoulinspired_list(
        sort_key: Literal["id", "reference_date"] = Query(default='id'),
        sort_type: Literal["DESC", "ASC"] = Query(default='DESC'),
        page: int = Query(default=1),
        item_per_page: int = Query(default=10),

        usecase: USECASE_TYPE = Depends(SeoulInspiredUsecase)
):
    seoulinspired_items, seoulinspired_total_count = usecase.get_content_list(
        sort_key=sort_key,
        sort_type=sort_type,
        page=page,
        item_per_page=item_per_page
    )
    return JSONResponse(
        status_code=200,
        content={
            "sort_key": sort_key,
            "sort_type": sort_type,
            "page": page,
            "item_per_page": item_per_page,
            "total_count": seoulinspired_total_count,
            "items": [{
                "id": seoulinspired_item.id,
                "trace_id": seoulinspired_item.trace_id,
                "reference_id": seoulinspired_item.reference_id,
                "reference_date": seoulinspired_item.reference_date.isoformat(),
                "reference_link": seoulinspired_item.reference_link,
                "thumbnail": seoulinspired_item.thumbnail,
                "is_convert": seoulinspired_item.is_convert,
                "title": seoulinspired_item.title
            } for seoulinspired_item in seoulinspired_items]
        })


@seoulinspired_router.get(path="/seoulinspired/{trace_id:str}")
def seoulinspired_content_retreieve(
        trace_id: str = Path(),
        usecase: USECASE_TYPE = Depends(SeoulInspiredUsecase)
):
    seoulinspired = usecase.get_content(trace_id=trace_id)
    if seoulinspired is None:
        return JSONResponse(status_code=404, content={})

    return JSONResponse(
        status_code=200,
        content={
            "id": seoulinspired.id,
            "trace_id": seoulinspired.trace_id,
            "reference_id": seoulinspired.reference_id,
            "reference_date": seoulinspired.reference_date.isoformat(),
            "reference_link": seoulinspired.reference_link,
            "thumbnail": seoulinspired.thumbnail,
            "is_convert": seoulinspired.is_convert,
            "title": seoulinspired.title,
            "content": seoulinspired.content
        })


@seoulinspired_router.post(path="/seoulinspired/{trace_id:str}/convert")
def seoulinspired_content_convert(
        trace_id: str = Path(),
        usecase: USECASE_TYPE = Depends(SeoulInspiredUsecase)
):
    return JSONResponse(status_code=200, content=usecase.convert(trace_id=trace_id))
