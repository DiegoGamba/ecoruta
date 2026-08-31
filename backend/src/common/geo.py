"""Utilidades geoespaciales: geohash y agrupamiento de reportes.

Se implementa geohash sin dependencias externas para mantener el paquete de
despliegue de Lambda liviano (arranque en frío menor) y auditable.
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Sequence

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
EARTH_RADIUS_M = 6_371_000.0


def encode_geohash(lat: float, lon: float, precision: int = 7) -> str:
    """Codifica una coordenada en geohash.

    Precisión 7 ≈ celdas de 153 m x 153 m, adecuada para agrupar puntos
    críticos a escala de manzana urbana.
    """
    validate_coordinates(lat, lon)
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    hash_chars: list[str] = []
    bits = 0
    bit_count = 0
    even_bit = True

    while len(hash_chars) < precision:
        if even_bit:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon > mid:
                bits = (bits << 1) | 1
                lon_range[0] = mid
            else:
                bits <<= 1
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat > mid:
                bits = (bits << 1) | 1
                lat_range[0] = mid
            else:
                bits <<= 1
                lat_range[1] = mid
        even_bit = not even_bit
        bit_count += 1
        if bit_count == 5:
            hash_chars.append(_BASE32[bits])
            bits = 0
            bit_count = 0

    return "".join(hash_chars)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia sobre la superficie terrestre en metros."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def validate_coordinates(lat: float, lon: float) -> None:
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("latitud fuera de rango [-90, 90]")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("longitud fuera de rango [-180, 180]")


def cluster_reports(
    reports: Sequence[dict],
    radius_m: int = 120,
    min_reports: int = 3,
) -> list[dict]:
    """Agrupa reportes cercanos en puntos críticos (variante de DBSCAN espacial).

    Algoritmo: se recorren los reportes ordenados por antigüedad; cada reporte
    no asignado abre un cluster y absorbe a todos los vecinos dentro de
    `radius_m`. Complejidad O(n²) acotada por el prefiltrado por geohash que
    hace la capa de datos, suficiente para el volumen por localidad.

    Devuelve solo clusters con al menos `min_reports` reportes, ordenados de
    mayor a menor severidad acumulada.
    """
    pending = list(reports)
    clusters: list[dict] = []

    while pending:
        seed = pending.pop(0)
        members = [seed]
        remaining: list[dict] = []
        for candidate in pending:
            distance = haversine_m(
                float(seed["lat"]), float(seed["lon"]),
                float(candidate["lat"]), float(candidate["lon"]),
            )
            (members if distance <= radius_m else remaining).append(candidate)
        pending = remaining

        if len(members) < min_reports:
            continue

        clusters.append(_summarize_cluster(members))

    clusters.sort(key=lambda c: c["severity_score"], reverse=True)
    return clusters


def _summarize_cluster(members: Sequence[dict]) -> dict:
    lat = sum(float(m["lat"]) for m in members) / len(members)
    lon = sum(float(m["lon"]) for m in members) / len(members)
    severity = sum(int(m.get("severity", 1)) for m in members)
    categories: dict[str, int] = defaultdict(int)
    for m in members:
        categories[str(m.get("category", "no_clasificado"))] += 1
    return {
        "centroid": {"lat": round(lat, 6), "lon": round(lon, 6)},
        "geohash": encode_geohash(lat, lon),
        "report_count": len(members),
        "severity_score": severity,
        "dominant_category": max(categories.items(), key=lambda kv: kv[1])[0],
        "category_breakdown": dict(categories),
        "report_ids": [m["report_id"] for m in members],
    }


def bounding_geohashes(lat: float, lon: float, precision: int = 6) -> list[str]:
    """Geohashes de la celda y sus vecinos aproximados, para consultas por zona."""
    validate_coordinates(lat, lon)
    step = 0.01  # ≈ 1.1 km, cubre la celda de precisión 6 y sus adyacentes
    offsets: Iterable[tuple[float, float]] = (
        (dy * step, dx * step) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
    )
    seen: list[str] = []
    for dlat, dlon in offsets:
        nlat = max(-90.0, min(90.0, lat + dlat))
        nlon = max(-180.0, min(180.0, lon + dlon))
        gh = encode_geohash(nlat, nlon, precision)
        if gh not in seen:
            seen.append(gh)
    return seen
