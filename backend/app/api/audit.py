from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import require_reader
from app.database.dependency import get_session
from app.domain.audit.repository import ChangeRecordRepository
from app.domain.audit.schema import ChangeRecordResponse
from app.domain.audit.service import ChangeRecordService


router = APIRouter(prefix="/changes", tags=["changes"], dependencies=[Depends(require_reader)])


def get_audit_service(session: Session) -> ChangeRecordService:
    return ChangeRecordService(ChangeRecordRepository(session))


@router.get("", response_model=list[ChangeRecordResponse])
def list_changes(
    entity_type: str | None = None,
    entity_id: str | None = None,
    changed_by: str | None = None,
    session: Session = Depends(get_session),
):
    return get_audit_service(session).list_changes(entity_type, entity_id, changed_by)


@router.get("/{change_id}", response_model=ChangeRecordResponse)
def get_change(change_id: str, session: Session = Depends(get_session)):
    change = get_audit_service(session).get_change(change_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Change record not found")
    return change
