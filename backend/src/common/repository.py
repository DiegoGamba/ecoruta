"""Capa de acceso a datos (patrón Repository) sobre DynamoDB single-table.

Aislar boto3 aquí permite: (1) probar la lógica de negocio con un doble en
memoria, y (2) cambiar el motor de persistencia sin tocar los handlers.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC
from decimal import Decimal
from typing import Any, Protocol

from .geo import bounding_geohashes
from .models import Report


def _clean(value: Any) -> Any:
    """DynamoDB devuelve Decimal; se normaliza a tipos nativos de Python."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    return value


def _to_dynamo(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [_to_dynamo(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_dynamo(v) for k, v in value.items()}
    return value


class ReportRepository(Protocol):
    def save(self, report: Report) -> dict: ...
    def get(self, report_id: str) -> dict: ...
    def update_status(self, report_id: str, target: str, actor: str) -> dict: ...
    def list_by_area(self, lat: float, lon: float, limit: int = 200) -> list[dict]: ...
    def list_by_status(self, status: str, limit: int = 200) -> list[dict]: ...


class DynamoReportRepository:
    """Implementación real. `table` es un `boto3.resource('dynamodb').Table(...)`."""

    def __init__(self, table: Any) -> None:
        self._table = table

    def save(self, report: Report) -> dict:
        item = _to_dynamo(report.to_item())
        self._table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK)",
        )
        return _clean(item)

    def get(self, report_id: str) -> dict:
        result = self._table.get_item(Key={"PK": f"REPORT#{report_id}", "SK": "METADATA"})
        item = result.get("Item")
        if not item:
            raise KeyError(report_id)
        return _clean(item)

    def update_status(self, report_id: str, target: str, actor: str) -> dict:
        from datetime import datetime

        now = datetime.now(UTC).isoformat(timespec="seconds")
        result = self._table.update_item(
            Key={"PK": f"REPORT#{report_id}", "SK": "METADATA"},
            UpdateExpression=(
                "SET #s = :s, GSI2PK = :gp, updated_at = :u, last_actor = :a"
            ),
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": target,
                ":gp": f"STATUS#{target}",
                ":u": now,
                ":a": actor,
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="ALL_NEW",
        )
        return _clean(result["Attributes"])

    def list_by_area(self, lat: float, lon: float, limit: int = 200) -> list[dict]:
        from boto3.dynamodb.conditions import Key

        items: list[dict] = []
        for gh in bounding_geohashes(lat, lon):
            page = self._table.query(
                IndexName="GSI1",
                KeyConditionExpression=Key("GSI1PK").eq(f"GEO#{gh}"),
                Limit=limit,
                ScanIndexForward=False,
            )
            items.extend(_clean(i) for i in page.get("Items", []))
            if len(items) >= limit:
                break
        return items[:limit]

    def list_by_status(self, status: str, limit: int = 200) -> list[dict]:
        from boto3.dynamodb.conditions import Key

        page = self._table.query(
            IndexName="GSI2",
            KeyConditionExpression=Key("GSI2PK").eq(f"STATUS#{status}"),
            Limit=limit,
            ScanIndexForward=False,
        )
        return [_clean(i) for i in page.get("Items", [])]


class InMemoryReportRepository:
    """Doble de prueba con la misma semántica (usado por la suite de tests)."""

    def __init__(self, seed: Iterable[dict] | None = None) -> None:
        self._items: dict[str, dict] = {}
        for item in seed or []:
            self._items[item["report_id"]] = dict(item)

    def save(self, report: Report) -> dict:
        item = report.to_item()
        if item["report_id"] in self._items:
            raise ValueError("reporte duplicado")
        self._items[item["report_id"]] = item
        return item

    def get(self, report_id: str) -> dict:
        if report_id not in self._items:
            raise KeyError(report_id)
        return self._items[report_id]

    def update_status(self, report_id: str, target: str, actor: str) -> dict:
        item = self.get(report_id)
        item["status"] = target
        item["GSI2PK"] = f"STATUS#{target}"
        item["last_actor"] = actor
        return item

    def list_by_area(self, lat: float, lon: float, limit: int = 200) -> list[dict]:
        zone = set(bounding_geohashes(lat, lon))
        return [i for i in self._items.values() if i["geohash"][:6] in zone][:limit]

    def list_by_status(self, status: str, limit: int = 200) -> list[dict]:
        return [i for i in self._items.values() if i["status"] == status][:limit]
