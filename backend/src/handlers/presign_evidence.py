"""POST /evidencias/url — entrega una URL prefirmada para subir la foto a S3.

La app nunca recibe credenciales de AWS ni sube el archivo a través de la API:
sube directo a S3 con una URL de vida corta, restringida por tipo y tamaño.
Esto evita el límite de 6 MB de payload de Lambda y reduce costo de tránsito.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from ..common.config import get_settings
from ..common.http import audit, get_user_id, handler_wrapper, parse_body, response
from ..common.logging_utils import pseudonymize
from ..common.models import ValidationError
from .deps import get_s3

ALLOWED_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@handler_wrapper
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    settings = get_settings()
    user_id = get_user_id(event)
    body = parse_body(event)

    content_type = str(body.get("content_type", "")).lower()
    if content_type not in ALLOWED_TYPES:
        raise ValidationError(f"content_type no permitido; use {sorted(ALLOWED_TYPES)}")

    try:
        size = int(body.get("size_bytes", 0))
    except (TypeError, ValueError) as exc:
        raise ValidationError("size_bytes debe ser un entero") from exc
    if not 0 < size <= settings.max_evidence_bytes:
        raise ValidationError(f"la evidencia debe pesar entre 1 y {settings.max_evidence_bytes} bytes")

    today = datetime.now(UTC).strftime("%Y/%m/%d")
    key = f"evidencias/{today}/{pseudonymize(user_id)}/{uuid.uuid4()}.{ALLOWED_TYPES[content_type]}"

    url = get_s3().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.evidence_bucket,
            "Key": key,
            "ContentType": content_type,
            "ContentLength": size,
            "ServerSideEncryption": "aws:kms",
        },
        ExpiresIn=settings.presign_ttl_seconds,
    )
    audit("presign_evidencia", user_id, key=key)
    return response(
        201,
        {"upload_url": url, "evidence_key": key, "expires_in": settings.presign_ttl_seconds},
    )
