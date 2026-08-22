import base64
import binascii
import json
from dataclasses import dataclass
from json import JSONDecodeError

from fastapi import Depends, Header, HTTPException

from app.config.settings import settings


READER_ROLE = "CMDB.Reader"
ADMIN_ROLE = "CMDB.Admin"
OBJECT_ID_CLAIMS = {
    "oid",
    "http://schemas.microsoft.com/identity/claims/objectidentifier",
}


@dataclass(frozen=True)
class Principal:
    actor: str
    roles: frozenset[str]


def _decode_easy_auth_principal(value: str) -> dict:
    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid Entra principal header") from exc

    try:
        payload = json.loads(decoded)
    except JSONDecodeError as exc:
        raise HTTPException(status_code=401, detail="Invalid Entra principal header") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=401, detail="Invalid Entra principal header")
    return payload


def parse_easy_auth_principal(value: str) -> Principal:
    payload = _decode_easy_auth_principal(value)
    if payload.get("auth_typ") != "aad":
        raise HTTPException(status_code=401, detail="Entra authentication required")

    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise HTTPException(status_code=401, detail="Entra principal claims are missing")

    role_type = payload.get("role_typ") or "roles"
    name_type = payload.get("name_typ")
    roles: set[str] = set()
    object_id: str | None = None
    fallback_actor: str | None = None

    for claim in claims:
        if not isinstance(claim, dict):
            raise HTTPException(status_code=401, detail="Invalid Entra principal claim")
        claim_type = claim.get("typ")
        claim_value = claim.get("val")
        if not isinstance(claim_type, str) or not isinstance(claim_value, str):
            raise HTTPException(status_code=401, detail="Invalid Entra principal claim")
        if claim_type == role_type:
            roles.add(claim_value)
        if claim_type in OBJECT_ID_CLAIMS:
            object_id = claim_value
        if name_type and claim_type == name_type:
            fallback_actor = claim_value

    actor = object_id or fallback_actor
    if actor is None:
        raise HTTPException(status_code=401, detail="Entra principal identity is missing")
    if len(actor) > 255:
        raise HTTPException(status_code=401, detail="Entra principal identity is too long")

    return Principal(actor=actor, roles=frozenset(roles))


def current_principal(
    easy_auth_principal: str | None = Header(default=None, alias="X-MS-CLIENT-PRINCIPAL"),
    local_actor: str | None = Header(default=None, alias="X-CMDB-Actor", max_length=255),
) -> Principal:
    if settings.auth_mode == "entra":
        if easy_auth_principal is None:
            raise HTTPException(status_code=401, detail="Entra authentication required")
        return parse_easy_auth_principal(easy_auth_principal)

    if local_actor is None:
        return Principal(actor="local-readonly", roles=frozenset({READER_ROLE}))
    return Principal(actor=local_actor, roles=frozenset({READER_ROLE, ADMIN_ROLE}))


def require_reader(principal: Principal = Depends(current_principal)) -> Principal:
    if principal.roles.isdisjoint({READER_ROLE, ADMIN_ROLE}):
        raise HTTPException(status_code=403, detail="CMDB.Reader or CMDB.Admin role required")
    return principal


def require_admin(principal: Principal = Depends(current_principal)) -> Principal:
    if ADMIN_ROLE not in principal.roles:
        if settings.auth_mode == "local":
            raise HTTPException(status_code=401, detail="X-CMDB-Actor is required in local mode")
        raise HTTPException(status_code=403, detail="CMDB.Admin role required")
    return principal
