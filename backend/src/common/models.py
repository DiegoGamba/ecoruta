"""Modelos de dominio y validación de entrada.

La validación se hace explícita y sin dependencias externas para que cualquier
entrada malformada se rechace en el borde de la Lambda (fail fast) antes de
tocar DynamoDB.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .geo import encode_geohash, validate_coordinates

CATEGORIES = (
    "escombros",
    "organicos",
    "reciclables",
    "voluminosos",
    "peligrosos",
    "no_clasificado",
)

STATUSES = ("reportado", "verificado", "programado", "atendido", "descartado")

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
MAX_DESCRIPTION = 500
RETENTION_DAYS = 540


class ValidationError(ValueError):
    """Entrada inválida enviada por el cliente (se traduce a HTTP 400)."""


@dataclass
class Report:
    report_id: str
    user_id: str
    lat: float
    lon: float
    geohash: str
    category: str
    severity: int
    description: str
    status: str
    evidence_key: str | None
    created_at: str
    updated_at: str
    ttl: int
    locality: str | None = None
    ai_labels: list[str] = field(default_factory=list)

    def to_item(self) -> dict[str, Any]:
        """Representación single-table para DynamoDB."""
        item = asdict(self)
        item.update(
            {
                "PK": f"REPORT#{self.report_id}",
                "SK": "METADATA",
                "GSI1PK": f"GEO#{self.geohash[:6]}",
                "GSI1SK": f"{self.created_at}#{self.report_id}",
                "GSI2PK": f"STATUS#{self.status}",
                "GSI2SK": self.created_at,
                "entity": "Report",
            }
        )
        if self.evidence_key:
            # Índice disperso: solo los reportes con evidencia participan en GSI3.
            item["GSI3PK"] = f"EVID#{self.evidence_key}"
            item["GSI3SK"] = self.created_at
        return item

    def to_public(self) -> dict[str, Any]:
        """Vista expuesta por la API: sin identificador directo del usuario."""
        data = asdict(self)
        data.pop("user_id", None)
        data.pop("ttl", None)
        return data


def _require(payload: dict[str, Any], key: str) -> Any:
    if key not in payload or payload[key] in (None, ""):
        raise ValidationError(f"campo requerido faltante: {key}")
    return payload[key]


def _as_float(value: Any, key: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{key} debe ser numérico") from exc


def build_report(payload: dict[str, Any], user_id: str, now: datetime | None = None) -> Report:
    """Valida el payload del cliente y construye un `Report` consistente."""
    if not isinstance(payload, dict):
        raise ValidationError("el cuerpo debe ser un objeto JSON")
    if not _ID_RE.match(user_id or ""):
        raise ValidationError("identificador de usuario inválido")

    lat = _as_float(_require(payload, "lat"), "lat")
    lon = _as_float(_require(payload, "lon"), "lon")
    try:
        validate_coordinates(lat, lon)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    category = str(payload.get("category", "no_clasificado")).strip().lower()
    if category not in CATEGORIES:
        raise ValidationError(f"categoría inválida; use una de {list(CATEGORIES)}")

    try:
        severity = int(payload.get("severity", 1))
    except (TypeError, ValueError) as exc:
        raise ValidationError("severity debe ser un entero entre 1 y 5") from exc
    if not 1 <= severity <= 5:
        raise ValidationError("severity debe estar entre 1 y 5")

    description = str(payload.get("description", "")).strip()
    if len(description) > MAX_DESCRIPTION:
        raise ValidationError(f"description supera {MAX_DESCRIPTION} caracteres")

    evidence_key = payload.get("evidence_key")
    if evidence_key is not None:
        evidence_key = str(evidence_key)
        if ".." in evidence_key or evidence_key.startswith("/"):
            raise ValidationError("evidence_key inválida")

    moment = now or datetime.now(timezone.utc)
    timestamp = moment.isoformat(timespec="seconds")
    expires = moment + timedelta(days=RETENTION_DAYS)

    return Report(
        report_id=str(uuid.uuid4()),
        user_id=user_id,
        lat=round(lat, 6),
        lon=round(lon, 6),
        geohash=encode_geohash(lat, lon),
        category=category,
        severity=severity,
        description=description,
        status="reportado",
        evidence_key=evidence_key,
        created_at=timestamp,
        updated_at=timestamp,
        ttl=int(expires.timestamp()),
        locality=(str(payload["locality"])[:80] if payload.get("locality") else None),
    )


def validate_status_transition(current: str, target: str) -> None:
    """Solo se permiten transiciones hacia adelante del ciclo operativo."""
    if target not in STATUSES:
        raise ValidationError(f"estado inválido; use uno de {list(STATUSES)}")
    allowed = {
        "reportado": {"verificado", "descartado"},
        "verificado": {"programado", "descartado"},
        "programado": {"atendido"},
        "atendido": set(),
        "descartado": set(),
    }
    if target not in allowed.get(current, set()):
        raise ValidationError(f"transición no permitida: {current} -> {target}")
