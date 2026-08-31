"""Logging estructurado en JSON, apto para CloudWatch Logs Insights.

Se evita imprimir datos personales: el `user_id` se registra como hash corto y
nunca se escriben coordenadas exactas en nivel INFO.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def log(logger: logging.Logger, level: int, msg: str, **fields: Any) -> None:
    logger.log(level, msg, extra={"extra_fields": fields})


def pseudonymize(value: str) -> str:
    """Hash corto y estable para correlacionar sin exponer identidad."""
    if not value:
        return "anon"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
