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
        if not isinstance(item, dict):
            continue
        name = item.get("name", {})
        if isinstance(name, dict) and (
            name.get("value") == resource_name
            or name.get("localizedValue") == resource_name
        ):
            return item
    raise ValueError(f"quota usage entry not found: {resource_name}")


def _numbers(item: dict[str, Any]) -> tuple[float, float]:
    return float(item.get("currentValue", 0)), float(item.get("limit", 0))


def regional_decision(document: dict[str, Any], *, resource_name: str, environment_exists: bool, minimum_limit: int, request_increment: int) -> dict[str, Any]:
    item = _usage_item(document, resource_name)
    current, limit = _numbers(item)
    available = limit - current
    if environment_exists or available >= 1:
        return {"resourceName": resource_name, "current": current, "limit": limit, "available": available, "environmentExists": environment_exists, "action": "ok", "requestedLimit": None}
    requested_limit = max(int(minimum_limit), math.ceil(current + 1), math.ceil(limit) + int(request_increment))
    return {"resourceName": resource_name, "current": current, "limit": limit, "available": available, "environmentExists": environment_exists, "action": "request", "requestedLimit": requested_limit}


def environment_decision(document: dict[str, Any], *, resource_name: str, required_available: float) -> dict[str, Any]:
    item = _usage_item(document, resource_name)
    current, limit = _numbers(item)
    available = limit - current
    return {"resourceName": resource_name, "current": current, "limit": limit, "available": available, "requiredAvailable": required_available, "action": "ok" if available >= required_available else "manual_request"}


def _parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("regional")
    r.add_argument("--usage-file", required=True)
    r.add_argument("--resource-name", default="ManagedEnvironmentCount")
    r.add_argument("--environment-exists", required=True)
    r.add_argument("--minimum-limit", type=int, required=True)
    r.add_argument("--request-increment", type=int, required=True)
    e = sub.add_parser("environment")
    e.add_argument("--usage-file", required=True)
    e.add_argument("--resource-name", default="ManagedEnvironmentConsumptionCores")
    e.add_argument("--required-available", type=float, required=True)
    return parser


def main():
    args = _parser().parse_args()
    document = _load_usage(args.usage_file)
    if args.mode == "regional":
        result = regional_decision(document, resource_name=args.resource_name, environment_exists=args.environment_exists == "true", minimum_limit=args.minimum_limit, request_increment=args.request_increment)
    else:
        result = environment_decision(document, resource_name=args.resource_name, required_available=args.required_available)
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
