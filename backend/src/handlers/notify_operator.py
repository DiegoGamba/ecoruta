"""Notificación al operador de aseo (disparada por EventBridge).

Regla de negocio: se notifica de inmediato cuando el reporte es de categoría
`peligrosos` o cuando la severidad declarada es alta (>= 4). El resto entra al
consolidado diario, para no saturar al operador con ruido.
"""
from __future__ import annotations

import json
from typing import Any

from ..common.config import get_settings
from ..common.logging_utils import get_logger, log

logger = get_logger(__name__)

URGENT_CATEGORIES = {"peligrosos"}
URGENT_SEVERITY = 4


def is_urgent(detail: dict) -> bool:
    if str(detail.get("category", "")) in URGENT_CATEGORIES:
        return True
    try:
        return int(detail.get("severity", 0)) >= URGENT_SEVERITY
    except (TypeError, ValueError):
        return False


def build_message(detail: dict) -> str:
    return json.dumps(
        {
            "titulo": "Reporte prioritario de residuos",
            "report_id": detail.get("report_id"),
            "categoria": detail.get("category"),
            "severidad": detail.get("severity"),
            "zona": detail.get("geohash"),
        },
        ensure_ascii=False,
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    import boto3

    settings = get_settings()
    detail = event.get("detail", {}) or {}

    if not is_urgent(detail):
        log(logger, 20, "reporte no prioritario, se omite alerta",
            report_id=detail.get("report_id"))
        return {"notified": False}

    if not settings.alert_topic_arn:
        log(logger, 30, "ALERT_TOPIC_ARN no configurado")
        return {"notified": False}

    boto3.client("sns", region_name=settings.region).publish(
        TopicArn=settings.alert_topic_arn,
        Subject="EcoRuta | Reporte prioritario",
        Message=build_message(detail),
    )
    log(logger, 20, "alerta enviada", report_id=detail.get("report_id"))
    return {"notified": True}
