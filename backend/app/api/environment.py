from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependency import get_session
from app.domain.environment.repository import EnvironmentRepository
from app.domain.environment.schema import EnvironmentCreate, EnvironmentResponse
from app.domain.environment.service import EnvironmentService

router = APIRouter(prefix="/environments", tags=["environments"])


@router.get("", response_model=list[EnvironmentResponse])
def list_environments(session: Session = Depends(get_session)):
    service = EnvironmentService(EnvironmentRepository(session))
    return service.list_environments()


@router.post("", response_model=EnvironmentResponse)
def create_environment(
    data: EnvironmentCreate,
    session: Session = Depends(get_session),
):
    service = EnvironmentService(EnvironmentRepository(session))
    return service.create_environment(data)
