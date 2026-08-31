"""PATCH /reportes/{id}/estado — transición de estado (solo grupo `operadores`)."""
from __future__ import annotations

from typing import Any

from ..common.http import (
    audit,
    get_user_id,
    handler_wrapper,
    parse_body,
    require_group,
    response,
)
from ..common.models import ValidationError
from .deps import get_service


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    require_group(event, "operadores")
    actor = get_user_id(event)
    report_id = (event.get("pathParameters") or {}).get("id")
    if not report_id:
        raise ValidationError("falta el identificador del reporte")

    target = str(parse_body(event).get("status", "")).strip().lower()
    updated = get_service().change_status(report_id, target, actor)
    audit("cambiar_estado", actor, report_id=report_id, status=target)
    return response(200, updated)
