from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependency import get_session
from app.domain.team.repository import TeamRepository
from app.domain.team.schema import TeamCreate, TeamResponse
from app.domain.team.service import TeamService


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamResponse])
def list_teams(session: Session = Depends(get_session)):
    service = TeamService(TeamRepository(session))
    return service.list_teams()


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: str, session: Session = Depends(get_session)):
    service = TeamService(TeamRepository(session))
    team = service.get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="team not found")
    return team


@router.post("", response_model=TeamResponse)
def create_team(payload: TeamCreate, session: Session = Depends(get_session)):
    service = TeamService(TeamRepository(session))
    return service.create_team(payload)
