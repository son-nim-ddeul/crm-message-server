from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from . import service, schemas, exceptions
from .dependencies import get_db

router = APIRouter()


@router.post(
    "/references",
    response_model=schemas.MessageReferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="메시지 레퍼런스 생성",
    description="새로운 메시지 레퍼런스를 생성합니다."
)
async def create_reference(ref: schemas.MessageReferenceCreate, db: Session = Depends(get_db)):
    return service.create_message_reference(db=db, ref=ref)


@router.get(
    "/references/{reference_id}",
    response_model=schemas.MessageReferenceResponse,
    summary="메시지 레퍼런스 상세 조회",
    description="특정 ID의 메시지 레퍼런스 정보를 조회합니다."
)
async def get_reference(reference_id: int, db: Session = Depends(get_db)):
    db_ref = service.get_message_reference(db=db, reference_id=reference_id)
    if db_ref is None:
        raise exceptions.MessageReferenceNotFound()
    return db_ref

