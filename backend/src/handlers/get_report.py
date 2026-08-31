"""GET /reportes/{id} — consulta el detalle de un reporte."""
from __future__ import annotations

from typing import Any

from ..common.http import handler_wrapper, response
from ..common.models import ValidationError
from .deps import get_service


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    report_id = (event.get("pathParameters") or {}).get("id")
    if not report_id:
        raise ValidationError("falta el identificador del reporte")
    return response(200, get_service().get(report_id))
