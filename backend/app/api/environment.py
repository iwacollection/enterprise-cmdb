from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependency import get_session
from app.domain.environment.repository import EnvironmentRepository
from app.domain.environment.schema import EnvironmentCreate, EnvironmentResponse, EnvironmentUpdate
from app.domain.environment.service import EnvironmentService

router = APIRouter(prefix="/environments", tags=["environments"])


def get_service(session: Session) -> EnvironmentService:
    return EnvironmentService(EnvironmentRepository(session))


@router.get("", response_model=list[EnvironmentResponse])
def list_environments(session: Session = Depends(get_session)):
    return get_service(session).list_environments()


@router.get("/{environment_id}", response_model=EnvironmentResponse)
def get_environment(environment_id: UUID, session: Session = Depends(get_session)):
    environment = get_service(session).get_environment(environment_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return environment


@router.post("", response_model=EnvironmentResponse, status_code=201)
def create_environment(
    data: EnvironmentCreate,
    session: Session = Depends(get_session),
):
    return get_service(session).create_environment(data)


@router.put("/{environment_id}", response_model=EnvironmentResponse)
def update_environment(
    environment_id: UUID,
    data: EnvironmentUpdate,
    session: Session = Depends(get_session),
):
    service = get_service(session)
    environment = service.get_environment(environment_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return service.update_environment(environment, data)
