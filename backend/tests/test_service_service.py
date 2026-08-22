from app.domain.service.schema import ServiceCreate, ServiceUpdate
from app.domain.service.service import ServiceService


class FakeRepository:
    def __init__(self):
        self.service = None
        self.audit = []

    def list(self):
        return [] if self.service is None else [self.service]

    def get_by_id(self, service_id):
        if self.service is not None and self.service.id == service_id:
            return self.service
        return None

    def create(self, service, request_id, changed_by):
        self.service = service
        self.audit.append(("create", request_id, changed_by))
        return service

    def update(self, service, before, request_id, changed_by):
        self.service = service
        self.audit.append(("update", request_id, changed_by, before))
        return service

    def delete(self, service, request_id, changed_by):
        self.audit.append(("delete", request_id, changed_by))
        self.service = None


def test_service_service_crud_contract():
    repository = FakeRepository()
    layer = ServiceService(repository)

    created = layer.create_service(
        ServiceCreate(name="cmdb-api", team_id="team-1", description="api"),
        "request-create",
        "alice@example.com",
    )
    created.id = "service-1"
    assert layer.get_service("service-1") is created

    updated = layer.update_service(
        created,
        ServiceUpdate(name="cmdb", team_id="team-2", description="core service"),
        "request-update",
        "bob@example.com",
    )
    assert updated.name == "cmdb"
    assert updated.team_id == "team-2"

    layer.delete_service(updated, "request-delete", "carol@example.com")
    assert layer.get_service("service-1") is None
    assert [entry[0] for entry in repository.audit] == ["create", "update", "delete"]
