from app.domain.service.model import Service
from app.domain.service.repository import ServiceRepository
from app.domain.service.schema import ServiceCreate, ServiceUpdate


class ServiceService:
    def __init__(self, repository: ServiceRepository):
        self.repository = repository

    def list_services(self) -> list[Service]:
        return self.repository.list()

    def get_service(self, service_id: str) -> Service | None:
        return self.repository.get_by_id(service_id)

    def create_service(self, data: ServiceCreate) -> Service:
        return self.repository.create(
            Service(
                name=data.name,
                team_id=data.team_id,
                description=data.description,
            )
        )

    def update_service(self, service: Service, data: ServiceUpdate) -> Service:
        service.name = data.name
        service.team_id = data.team_id
        service.description = data.description
        return self.repository.update(service)

    def delete_service(self, service: Service) -> None:
        self.repository.delete(service)
