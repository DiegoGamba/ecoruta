"""Clasificación asistida de la evidencia (disparada por evento de S3).

Rekognition sugiere etiquetas sobre la foto y se mapean a las categorías del
dominio. La sugerencia NO reemplaza al ciudadano: se guarda como `ai_labels` y
solo se propone una categoría cuando la confianza supera el umbral. Es el
componente con mayor potencial de investigación del proyecto (línea base para
comparar contra un modelo propio entrenado con datos locales).
"""
from __future__ import annotations

import urllib.parse
from typing import Any

from ..common.config import get_settings
from ..common.logging_utils import get_logger, log

logger = get_logger(__name__)

CONFIDENCE_THRESHOLD = 70.0

LABEL_TO_CATEGORY: dict[str, str] = {
    "rubble": "escombros",
    "brick": "escombros",
    "concrete": "escombros",
    "soil": "escombros",
    "food": "organicos",
    "vegetable": "organicos",
    "leaf": "organicos",
    "plastic": "reciclables",
    "bottle": "reciclables",
    "cardboard": "reciclables",
    "can": "reciclables",
    "glass": "reciclables",
    "paper": "reciclables",
    "furniture": "voluminosos",
    "couch": "voluminosos",
    "mattress": "voluminosos",
    "appliance": "voluminosos",
    "tire": "voluminosos",
    "battery": "peligrosos",
    "syringe": "peligrosos",
    "paint": "peligrosos",
    "chemical": "peligrosos",
}


def map_labels_to_category(labels: list[dict]) -> tuple[str, list[str]]:
    """Devuelve (categoría sugerida, etiquetas por encima del umbral).

    Precedencia: `peligrosos` gana siempre porque define la ruta operativa y el
    protocolo de manejo; el resto se resuelve por confianza descendente.
    """
    confident = [l for l in labels if float(l.get("Confidence", 0)) >= CONFIDENCE_THRESHOLD]
    confident.sort(key=lambda l: float(l.get("Confidence", 0)), reverse=True)
    names = [str(l.get("Name", "")) for l in confident]

    mapped = [
        LABEL_TO_CATEGORY[n.lower()] for n in names if n.lower() in LABEL_TO_CATEGORY
    ]
    if "peligrosos" in mapped:
        return "peligrosos", names
    return (mapped[0] if mapped else "no_clasificado"), names


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    import boto3

    settings = get_settings()
    rekognition = boto3.client("rekognition", region_name=settings.region)
    table = boto3.resource("dynamodb", region_name=settings.region).Table(settings.table_name)

    processed = 0
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        try:
            detected = rekognition.detect_labels(
                Image={"S3Object": {"Bucket": bucket, "Name": key}},
                MaxLabels=15,
                MinConfidence=CONFIDENCE_THRESHOLD,
            )
        except Exception:  # noqa: BLE001 - una foto ilegible no debe frenar el lote
            logger.exception("no se pudo analizar la evidencia")
            continue

        category, names = map_labels_to_category(detected.get("Labels", []))
        report_id = _resolve_report_id(table, key)
        if not report_id:
            log(logger, 20, "evidencia sin reporte asociado aún", key=key)
            continue

        table.update_item(
            Key={"PK": f"REPORT#{report_id}", "SK": "METADATA"},
            UpdateExpression="SET ai_labels = :l, ai_category = :c",
            ExpressionAttributeValues={":l": names, ":c": category},
        )
        log(logger, 20, "evidencia clasificada", report_id=report_id, category=category)
        processed += 1

    return {"processed": processed}


def _resolve_report_id(table: Any, evidence_key: str) -> str | None:
    """Resuelve el reporte por índice `GSI3` (evidence_key -> reporte).

    Se usa un índice y no un `scan`: el scan crece linealmente con la tabla y su
    costo se vuelve inaceptable en producción.
    """
    from boto3.dynamodb.conditions import Key

    result = table.query(
        IndexName="GSI3",
        KeyConditionExpression=Key("GSI3PK").eq(f"EVID#{evidence_key}"),
        ProjectionExpression="report_id",
        Limit=1,
    )
    items = result.get("Items", [])
    return str(items[0]["report_id"]) if items else None
