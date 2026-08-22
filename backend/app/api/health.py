from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.dependency import get_session

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready(session: Session = Depends(get_session)):
    session.execute(text("SELECT 1")).scalar_one()
    return {"status": "ready"}
