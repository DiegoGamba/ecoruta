"""Composición de dependencias (inyección) compartida por los handlers.

Los clientes de AWS se crean una sola vez por contenedor de Lambda para
reutilizar la conexión TLS entre invocaciones y reducir la latencia.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from ..common.config import get_settings
from ..common.repository import DynamoReportRepository
from ..common.services import ReportService


@lru_cache(maxsize=1)
def _boto():
    import boto3

    return boto3


@lru_cache(maxsize=1)
def get_table() -> Any:
    settings = get_settings()
    return _boto().resource("dynamodb", region_name=settings.region).Table(settings.table_name)


@lru_cache(maxsize=1)
def get_s3() -> Any:
    return _boto().client("s3", region_name=get_settings().region)


class EventBridgePublisher:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = _boto().client("events", region_name=self._settings.region)

    def publish(self, detail_type: str, detail: dict) -> None:
        self._client.put_events(
            Entries=[
                {
                    "Source": "ecoruta.api",
                    "DetailType": detail_type,
                    "Detail": json.dumps(detail, ensure_ascii=False),
                    "EventBusName": self._settings.event_bus,
                }
            ]
        )


@lru_cache(maxsize=1)
def get_service() -> ReportService:
    return ReportService(DynamoReportRepository(get_table()), EventBridgePublisher())
