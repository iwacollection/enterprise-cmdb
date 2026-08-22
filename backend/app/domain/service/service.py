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

    def team_exists(self, team_id: str) -> bool:
        return self.repository.team_exists(team_id)

    def is_referenced(self, service_id: str) -> bool:
        return self.repository.is_referenced(service_id)

    def create_service(self, data: ServiceCreate, request_id: str, changed_by: str) -> Service:
        return self.repository.create(
            Service(
                name=data.name,
                team_id=data.team_id,
                description=data.description,
            ),
            request_id,
            changed_by,
        )

    def update_service(
        self,
        service: Service,
        data: ServiceUpdate,
        request_id: str,
        changed_by: str,
    ) -> Service:
        before = {
            "id": service.id,
            "name": service.name,
            "team_id": service.team_id,
            "description": service.description,
        }
        service.name = data.name
        service.team_id = data.team_id
        service.description = data.description
        return self.repository.update(service, before, request_id, changed_by)

    def delete_service(self, service: Service, request_id: str, changed_by: str) -> None:
        self.repository.delete(service, request_id, changed_by)
