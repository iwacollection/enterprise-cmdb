from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import require_reader
from app.api.context import request_context
from app.database.dependency import get_session
from app.domain.asset.repository import AssetRepository
from app.domain.asset.schema import (
    AssetCreate,
    AssetResponse,
    AssetStatus,
    AssetType,
    AssetUpdate,
)
from app.domain.asset.service import AssetService


router = APIRouter(prefix="/assets", tags=["assets"], dependencies=[Depends(require_reader)])


def get_asset_service(session: Session) -> AssetService:
    return AssetService(AssetRepository(session))


@router.get("", response_model=list[AssetResponse])
def list_assets(
    name: str | None = None,
    asset_type: AssetType | None = None,
    status: AssetStatus | None = None,
    environment_id: UUID | None = None,
    team_id: str | None = None,
    service_id: str | None = None,
    session: Session = Depends(get_session),
):
    return get_asset_service(session).list_assets(
        name=name,
        asset_type=asset_type,
        status=status,
        environment_id=environment_id,
        team_id=team_id,
        service_id=service_id,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, session: Session = Depends(get_session)):
    asset = get_asset_service(session).get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset(
    payload: AssetCreate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_asset_service(session)
    error = service.reference_error(payload)
    if error is not None:
        raise HTTPException(status_code=404, detail=error)
    actor, request_id = context
    return service.create_asset(payload, request_id, actor)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_asset_service(session)
    if service.get_asset(asset_id) is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    error = service.reference_error(payload)
    if error is not None:
        raise HTTPException(status_code=404, detail=error)
    actor, request_id = context
    return service.update_asset(asset_id, payload, request_id, actor)
