from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

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


router = APIRouter(prefix="/assets", tags=["assets"])


def get_asset_service(session: Session) -> AssetService:
    return AssetService(AssetRepository(session))


def request_context(
    actor: str = Header(alias="X-CMDB-Actor"),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> tuple[str, str]:
    return actor, request_id or str(uuid4())


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
    actor, request_id = context
    return get_asset_service(session).create_asset(payload, request_id, actor)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    actor, request_id = context
    asset = get_asset_service(session).update_asset(asset_id, payload, request_id, actor)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
