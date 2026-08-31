"""POST /reportes — registra un nuevo reporte ciudadano."""
from __future__ import annotations

from typing import Any

from ..common.http import audit, handler_wrapper, parse_body, get_user_id, response
from .deps import get_service


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    user_id = get_user_id(event)
    payload = parse_body(event)
    created = get_service().create(payload, user_id)
    audit("crear_reporte", user_id, report_id=created["report_id"])
    return response(201, created, {"Location": f"/reportes/{created['report_id']}"})
