from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.context import request_context
from app.database.dependency import get_session
from app.domain.service.repository import ServiceRepository
from app.domain.service.schema import ServiceCreate, ServiceResponse, ServiceUpdate
from app.domain.service.service import ServiceService


router = APIRouter(prefix="/services", tags=["services"])


def get_service_layer(session: Session) -> ServiceService:
    return ServiceService(ServiceRepository(session))


@router.get("", response_model=list[ServiceResponse])
def list_services(session: Session = Depends(get_session)):
    return get_service_layer(session).list_services()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: str, session: Session = Depends(get_session)):
    service = get_service_layer(session).get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("", response_model=ServiceResponse, status_code=201)
def create_service(
    payload: ServiceCreate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    layer = get_service_layer(session)
    if not layer.team_exists(payload.team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    actor, request_id = context
    return layer.create_service(payload, request_id, actor)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: str,
    payload: ServiceUpdate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    layer = get_service_layer(session)
    service = layer.get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    if not layer.team_exists(payload.team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    actor, request_id = context
    return layer.update_service(service, payload, request_id, actor)


@router.delete("/{service_id}", status_code=204)
def delete_service(
    service_id: str,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    layer = get_service_layer(session)
    service = layer.get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    if layer.is_referenced(service_id):
        raise HTTPException(status_code=409, detail="Service is still referenced by assets")
    actor, request_id = context
    layer.delete_service(service, request_id, actor)
    return Response(status_code=204)
