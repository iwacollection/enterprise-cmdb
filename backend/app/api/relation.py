from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database.dependency import get_session
from app.domain.relation.repository import AssetRelationRepository
from app.domain.relation.schema import AssetRelationCreate, AssetRelationResponse
from app.domain.relation.service import AssetRelationService


router = APIRouter(tags=["relations"])


def get_relation_service(session: Session) -> AssetRelationService:
    return AssetRelationService(AssetRelationRepository(session))


def request_context(
    actor: str = Header(alias="X-CMDB-Actor"),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> tuple[str, str]:
    return actor, request_id or str(uuid4())


@router.get("/assets/{asset_id}/relations", response_model=list[AssetRelationResponse])
def list_asset_relations(
    asset_id: str,
    direction: Literal["in", "out", "both"] = Query(default="both"),
    session: Session = Depends(get_session),
):
    service = get_relation_service(session)
    if not service.asset_exists(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return service.list_relations(asset_id, direction)


@router.get("/relations/{relation_id}", response_model=AssetRelationResponse)
def get_relation(relation_id: str, session: Session = Depends(get_session)):
    relation = get_relation_service(session).get_relation(relation_id)
    if relation is None:
        raise HTTPException(status_code=404, detail="Relation not found")
    return relation


@router.post("/relations", response_model=AssetRelationResponse, status_code=201)
def create_relation(
    payload: AssetRelationCreate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_relation_service(session)
    if not service.asset_exists(payload.source_asset_id):
        raise HTTPException(status_code=404, detail="Source asset not found")
    if not service.asset_exists(payload.target_asset_id):
        raise HTTPException(status_code=404, detail="Target asset not found")
    if service.relation_exists(payload):
        raise HTTPException(status_code=409, detail="Relation already exists")
    actor, request_id = context
    return service.create_relation(payload, request_id, actor)


@router.delete("/relations/{relation_id}", status_code=204)
def delete_relation(
    relation_id: str,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_relation_service(session)
    relation = service.get_relation(relation_id)
    if relation is None:
        raise HTTPException(status_code=404, detail="Relation not found")
    actor, request_id = context
    service.delete_relation(relation, request_id, actor)
    return Response(status_code=204)
