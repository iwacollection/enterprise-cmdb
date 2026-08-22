from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.service.model import Service


class ServiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Service]:
        return list(self.session.scalars(select(Service)).all())

    def get_by_id(self, service_id: str) -> Service | None:
        return self.session.get(Service, service_id)

    def create(self, service: Service) -> Service:
        self.session.add(service)
        self.session.commit()
        self.session.refresh(service)
        return service

    def update(self, service: Service) -> Service:
        self.session.commit()
        self.session.refresh(service)
        return service

    def delete(self, service: Service) -> None:
        self.session.delete(service)
        self.session.commit()
