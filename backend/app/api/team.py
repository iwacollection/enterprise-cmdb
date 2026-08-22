from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependency import get_session
from app.domain.team.schema import TeamCreate, TeamResponse
from app.domain.team.service import TeamService
from app.domain.team.repository import TeamRepository


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamResponse])
def list_teams(session: Session = Depends(get_session)):
    service = TeamService(TeamRepository(session))
    return service.list_teams()


@router.post("", response_model=TeamResponse)
def create_team(payload: TeamCreate, session: Session = Depends(get_session)):
    service = TeamService(TeamRepository(session))
    return service.create_team(payload)
