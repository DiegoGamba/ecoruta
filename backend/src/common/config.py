"""Configuración centralizada leída de variables de entorno.

Ningún secreto se escribe en código: todos los valores provienen del entorno
inyectado por Terraform (o de valores por defecto seguros para pruebas).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    table_name: str
    evidence_bucket: str
    event_bus: str
    alert_topic_arn: str
    region: str
    stage: str
    max_evidence_bytes: int
    presign_ttl_seconds: int
    cluster_radius_m: int
    cluster_min_reports: int
    log_level: str

    @property
    def is_prod(self) -> bool:
        return self.stage == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        table_name=os.environ.get("TABLE_NAME", "ecoruta-local"),
        evidence_bucket=os.environ.get("EVIDENCE_BUCKET", "ecoruta-evidencias-local"),
        event_bus=os.environ.get("EVENT_BUS", "ecoruta-bus-local"),
        alert_topic_arn=os.environ.get("ALERT_TOPIC_ARN", ""),
        region=os.environ.get("AWS_REGION", "us-east-1"),
        stage=os.environ.get("STAGE", "dev"),
        max_evidence_bytes=int(os.environ.get("MAX_EVIDENCE_BYTES", 5 * 1024 * 1024)),
        presign_ttl_seconds=int(os.environ.get("PRESIGN_TTL_SECONDS", 300)),
        cluster_radius_m=int(os.environ.get("CLUSTER_RADIUS_M", 120)),
        cluster_min_reports=int(os.environ.get("CLUSTER_MIN_REPORTS", 3)),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
