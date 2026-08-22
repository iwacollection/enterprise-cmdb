from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.auth import require_reader
from app.api.context import request_context
from app.database.dependency import get_session
from app.domain.team.repository import TeamRepository
from app.domain.team.schema import TeamCreate, TeamResponse, TeamUpdate
from app.domain.team.service import TeamService


router = APIRouter(prefix="/teams", tags=["teams"], dependencies=[Depends(require_reader)])


def get_service(session: Session) -> TeamService:
    return TeamService(TeamRepository(session))


@router.get("", response_model=list[TeamResponse])
def list_teams(session: Session = Depends(get_session)):
    return get_service(session).list_teams()


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: str, session: Session = Depends(get_session)):
    team = get_service(session).get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("", response_model=TeamResponse, status_code=201)
def create_team(
    payload: TeamCreate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_service(session)
    if service.name_in_use(payload.name):
        raise HTTPException(status_code=409, detail="Team name already exists")
    actor, request_id = context
    return service.create_team(payload, request_id, actor)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    payload: TeamUpdate,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_service(session)
    team = service.get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    if service.name_in_use(payload.name, team_id):
        raise HTTPException(status_code=409, detail="Team name already exists")
    actor, request_id = context
    return service.update_team(team, payload, request_id, actor)


@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: str,
    context: tuple[str, str] = Depends(request_context),
    session: Session = Depends(get_session),
):
    service = get_service(session)
    team = service.get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    if service.is_referenced(team_id):
        raise HTTPException(status_code=409, detail="Team is still referenced")
    actor, request_id = context
    service.delete_team(team, request_id, actor)
    return Response(status_code=204)
