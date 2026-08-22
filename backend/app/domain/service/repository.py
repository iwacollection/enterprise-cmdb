from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.asset.model import AssetService
from app.domain.audit.model import ChangeRecord
from app.domain.service.model import Service
from app.domain.team.model import Team


class ServiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Service]:
        return list(self.session.scalars(select(Service)).all())

    def get_by_id(self, service_id: str) -> Service | None:
        return self.session.get(Service, service_id)

    def team_exists(self, team_id: str) -> bool:
        return self.session.get(Team, team_id) is not None

    def is_referenced(self, service_id: str) -> bool:
        statement = select(AssetService.asset_id).where(AssetService.service_id == service_id).limit(1)
        return self.session.scalar(statement) is not None

    def create(self, service: Service, request_id: str, changed_by: str) -> Service:
        self.session.add(service)
        self.session.flush()
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="service",
                entity_id=service.id,
                action="create",
                changed_by=changed_by,
                before=None,
                after=self._snapshot(service),
            )
        )
        self.session.commit()
        self.session.refresh(service)
        return service

    def update(
        self,
        service: Service,
        before: dict,
        request_id: str,
        changed_by: str,
    ) -> Service:
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="service",
                entity_id=service.id,
                action="update",
                changed_by=changed_by,
                before=before,
                after=self._snapshot(service),
            )
        )
        self.session.commit()
        self.session.refresh(service)
        return service

    def delete(self, service: Service, request_id: str, changed_by: str) -> None:
        before = self._snapshot(service)
        self.session.delete(service)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="service",
                entity_id=service.id,
                action="delete",
                changed_by=changed_by,
                before=before,
                after=None,
            )
        )
        self.session.commit()

    @staticmethod
    def _snapshot(service: Service) -> dict:
        return {
            "id": service.id,
            "name": service.name,
            "team_id": service.team_id,
            "description": service.description,
        }
