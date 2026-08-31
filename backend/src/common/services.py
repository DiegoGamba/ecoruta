"""Casos de uso. No conoce HTTP ni AWS: recibe el repositorio por inyección."""
from __future__ import annotations

from typing import Any, Protocol

from .geo import cluster_reports
from .models import Report, ValidationError, build_report, validate_status_transition


class EventPublisher(Protocol):
    def publish(self, detail_type: str, detail: dict) -> None: ...


class NullPublisher:
    """Publicador nulo para pruebas y ejecución local."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, dict]] = []

    def publish(self, detail_type: str, detail: dict) -> None:
        self.sent.append((detail_type, detail))


class ReportService:
    def __init__(self, repository: Any, publisher: EventPublisher | None = None) -> None:
        self._repo = repository
        self._publisher = publisher or NullPublisher()

    # Atributos internos que nunca salen por la API: claves de la tabla, el
    # identificador del ciudadano y metadatos de persistencia.
    _INTERNAL = {"user_id", "ttl", "entity"}

    @classmethod
    def _public(cls, item: dict) -> dict:
        return {
            k: v
            for k, v in item.items()
            if k not in cls._INTERNAL and not k.startswith(("PK", "SK", "GSI"))
        }

    def create(self, payload: dict, user_id: str) -> dict:
        report: Report = build_report(payload, user_id)
        stored = self._repo.save(report)
        self._publisher.publish(
            "ReporteCreado",
            {
                "report_id": report.report_id,
                "geohash": report.geohash,
                "category": report.category,
                "severity": report.severity,
            },
        )
        return self._public(stored)

    def get(self, report_id: str) -> dict:
        return self._public(self._repo.get(report_id))

    def change_status(self, report_id: str, target: str, actor: str) -> dict:
        current = self._repo.get(report_id)
        validate_status_transition(str(current["status"]), target)
        updated = self._repo.update_status(report_id, target, actor)
        self._publisher.publish(
            "EstadoActualizado", {"report_id": report_id, "status": target}
        )
        return self._public(updated)

    def hotspots(self, lat: float, lon: float, radius_m: int, min_reports: int) -> dict:
        candidates = [
            r
            for r in self._repo.list_by_area(lat, lon)
            if r.get("status") in {"reportado", "verificado"}
        ]
        clusters = cluster_reports(candidates, radius_m=radius_m, min_reports=min_reports)
        return {
            "center": {"lat": lat, "lon": lon},
            "params": {"radius_m": radius_m, "min_reports": min_reports},
            "analyzed_reports": len(candidates),
            "hotspot_count": len(clusters),
            "hotspots": clusters,
        }

    def indicators(self) -> dict:
        """KPIs operativos calculados sobre los índices por estado."""
        counts = {
            status: len(self._repo.list_by_status(status, limit=1000))
            for status in ("reportado", "verificado", "programado", "atendido", "descartado")
        }
        total = sum(counts.values())
        attended = counts["atendido"]
        return {
            "total_reportes": total,
            "por_estado": counts,
            "tasa_atencion": round(attended / total, 4) if total else 0.0,
            "pendientes": counts["reportado"] + counts["verificado"] + counts["programado"],
        }


def parse_float_param(params: dict[str, Any], key: str) -> float:
    if key not in params:
        raise ValidationError(f"parámetro requerido faltante: {key}")
    try:
        return float(params[key])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{key} debe ser numérico") from exc
