from uuid import uuid4

from fastapi import Header


def request_context(
    actor: str = Header(alias="X-CMDB-Actor", max_length=255),
    request_id: str | None = Header(default=None, alias="X-Request-ID", max_length=64),
) -> tuple[str, str]:
    return actor, request_id or str(uuid4())
