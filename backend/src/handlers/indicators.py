"""GET /indicadores — KPIs operativos para el panel de la entidad de aseo."""
from __future__ import annotations

from typing import Any

from ..common.http import handler_wrapper, require_group, response
from .deps import get_service


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    require_group(event, "operadores")
    return response(200, get_service().indicators(), {"Cache-Control": "max-age=120"})
