from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _load_usage(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _usage_item(document: dict[str, Any], resource_name: str) -> dict[str, Any]:
    for item in document.get("value", []):
        name = item.get("name", {})
        if name.get("value") == resource_name or name.get("localizedValue") == resource_name:
            return item
    raise ValueError(f"quota usage entry not found: {resource_name}")


def _numbers(item: dict[str, Any]) -> tuple[float, float]:
    current = float(item.get("currentValue", 0))
    limit = float(item.get("limit", 0))
    return current, limit


def regional_decision(
    document: dict[str, Any],
    *,
    resource_name: str,
    environment_exists: bool,
    minimum_limit: int,
    request_increment: int,
) -> dict[str, Any]:
    item = _usage_item(document, resource_name)
    current, limit = _numbers(item)
    available = limit - current

    if environment_exists:
        action = "ok"
        requested_limit = None
        reason = "target environment already exists; no additional regional environment slot is required"
    elif available >= 1:
        action = "ok"
        requested_limit = None
        reason = "regional managed-environment quota has at least one free slot"
    else:
        requested_limit = max(
            int(minimum_limit),
            math.ceil(current + 1),
            math.ceil(limit) + int(request_increment),
        )
        action = "request"
        reason = "regional managed-environment quota has no free slot"

    return {
        "resourceName": resource_name,
        "current": current,
        "limit": limit,
        "available": available,
        "environmentExists": environment_exists,
        "action": action,
        "requestedLimit": requested_limit,
        "reason": reason,
    }


def environment_decision(
    document: dict[str, Any],
    *,
    resource_name: str,
    required_available: float,
) -> dict[str, Any]:
    item = _usage_item(document, resource_name)
    current, limit = _numbers(item)
    available = limit - current
    action = "ok" if available >= required_available else "manual_request"
    reason = (
        "environment quota has enough free capacity"
        if action == "ok"
        else "environment quota requires a manual Azure Container Apps quota request"
    )
    return {
        "resourceName": resource_name,
        "current": current,
        "limit": limit,
        "available": available,
        "requiredAvailable": required_available,
        "action": action,
        "reason": reason,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Azure Container Apps quota usage for deployment.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    regional = subparsers.add_parser("regional")
    regional.add_argument("--usage-file", required=True)
    regional.add_argument("--resource-name", default="ManagedEnvironmentCount")
    regional.add_argument("--environment-exists", choices=("true", "false"), required=True)
    regional.add_argument("--minimum-limit", type=int, required=True)
    regional.add_argument("--request-increment", type=int, required=True)

    environment = subparsers.add_parser("environment")
    environment.add_argument("--usage-file", required=True)
    environment.add_argument("--resource-name", default="ManagedEnvironmentConsumptionCores")
    environment.add_argument("--required-available", type=float, required=True)

    return parser


def main() -> int:
    args = _parser().parse_args()
    document = _load_usage(args.usage_file)

    if args.mode == "regional":
        decision = regional_decision(
            document,
            resource_name=args.resource_name,
            environment_exists=args.environment_exists == "true",
            minimum_limit=args.minimum_limit,
            request_increment=args.request_increment,
        )
    else:
        decision = environment_decision(
            document,
            resource_name=args.resource_name,
            required_available=args.required_available,
        )

    print(json.dumps(decision, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
