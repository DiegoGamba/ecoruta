"""GET /puntos-criticos — agrupa reportes abiertos en puntos críticos priorizados."""
from __future__ import annotations

from typing import Any

from ..common.config import get_settings
from ..common.http import handler_wrapper, response
from ..common.services import parse_float_param
from .deps import get_service


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    settings = get_settings()
    params = event.get("queryStringParameters") or {}
    lat = parse_float_param(params, "lat")
    lon = parse_float_param(params, "lon")
    radius = int(params.get("radius_m", settings.cluster_radius_m))
    minimum = int(params.get("min_reports", settings.cluster_min_reports))
    radius = max(30, min(radius, 1000))
    minimum = max(2, min(minimum, 50))
    result = get_service().hotspots(lat, lon, radius, minimum)
    return response(200, result, {"Cache-Control": "max-age=60"})
