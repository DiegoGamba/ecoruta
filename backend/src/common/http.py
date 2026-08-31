"""Adaptadores HTTP para API Gateway (payload v2.0).

Centraliza parseo del evento, extracción de identidad desde el authorizer JWT
de Cognito y construcción de respuestas con cabeceras de seguridad.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from .logging_utils import get_logger, log, pseudonymize
from .models import ValidationError

logger = get_logger(__name__)

SECURITY_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


def response(status: int, body: Any, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {**SECURITY_HEADERS, **(headers or {})},
        "body": json.dumps(body, ensure_ascii=False, default=str),
    }


def parse_body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64

        raw = base64.b64decode(raw).decode("utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError("cuerpo JSON malformado") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("el cuerpo debe ser un objeto JSON")
    return parsed


def get_claims(event: dict[str, Any]) -> dict[str, Any]:
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )


def get_user_id(event: dict[str, Any]) -> str:
    claims = get_claims(event)
    user_id = claims.get("sub")
    if not user_id:
        raise PermissionError("token sin identificador de usuario")
    return str(user_id)


def get_groups(event: dict[str, Any]) -> set[str]:
    raw = get_claims(event).get("cognito:groups", "")
    if isinstance(raw, list):
        return {str(g) for g in raw}
    return {g for g in str(raw).replace("[", "").replace("]", "").split() if g}


def require_group(event: dict[str, Any], group: str) -> None:
    if group not in get_groups(event):
        raise PermissionError(f"se requiere pertenecer al grupo {group}")


def handler_wrapper(fn: Callable[[dict, Any], dict]) -> Callable[[dict, Any], dict]:
    """Decorador: traduce excepciones de dominio a códigos HTTP y registra la traza.

    Evita que un stacktrace o un mensaje interno llegue al cliente en un 500.
    """

    def wrapped(event: dict[str, Any], context: Any) -> dict[str, Any]:
        request_id = getattr(context, "aws_request_id", "local")
        try:
            return fn(event, context)
        except ValidationError as exc:
            log(logger, 20, "solicitud inválida", request_id=request_id, error=str(exc))
            return response(400, {"error": str(exc), "request_id": request_id})
        except PermissionError as exc:
            log(logger, 30, "acceso denegado", request_id=request_id, error=str(exc))
            return response(403, {"error": "acceso denegado", "request_id": request_id})
        except KeyError as exc:
            log(logger, 20, "recurso no encontrado", request_id=request_id, error=str(exc))
            return response(404, {"error": "recurso no encontrado", "request_id": request_id})
        except Exception:  # noqa: BLE001 - frontera de la Lambda
            logger.exception("error no controlado")
            return response(500, {"error": "error interno", "request_id": request_id})

    wrapped.__name__ = getattr(fn, "__name__", "handler")
    return wrapped


def audit(action: str, user_id: str, **fields: Any) -> None:
    log(logger, 20, "auditoria", action=action, actor=pseudonymize(user_id), **fields)
