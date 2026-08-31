import math

import pytest

from src.common.geo import (
    bounding_geohashes,
    cluster_reports,
    encode_geohash,
    haversine_m,
    validate_coordinates,
)


def r(rid, lat, lon, severity=1, category="reciclables", status="reportado"):
    return {
        "report_id": rid,
        "lat": lat,
        "lon": lon,
        "severity": severity,
        "category": category,
        "status": status,
    }


class TestGeohash:
    def test_conocido(self):
        # Referencia estándar: (57.64911, 10.40744) -> u4pruyd...
        assert encode_geohash(57.64911, 10.40744, 9).startswith("u4pruydqq")

    def test_bogota_es_estable(self):
        a = encode_geohash(4.710989, -74.072092)
        b = encode_geohash(4.710989, -74.072092)
        assert a == b and len(a) == 7

    def test_puntos_cercanos_comparten_prefijo(self):
        a = encode_geohash(4.710989, -74.072092, 6)
        b = encode_geohash(4.711100, -74.072150, 6)
        assert a == b

    def test_precision_controla_longitud(self):
        assert len(encode_geohash(4.7, -74.0, 4)) == 4

    @pytest.mark.parametrize("lat,lon", [(91, 0), (-91, 0), (0, 181), (0, -181)])
    def test_rechaza_coordenadas_invalidas(self, lat, lon):
        with pytest.raises(ValueError):
            validate_coordinates(lat, lon)


class TestHaversine:
    def test_distancia_cero(self):
        assert haversine_m(4.7, -74.0, 4.7, -74.0) == 0

    def test_un_grado_de_latitud(self):
        # 1° de latitud ≈ 111.19 km
        assert math.isclose(haversine_m(0, 0, 1, 0), 111_195, rel_tol=0.01)

    def test_simetria(self):
        assert haversine_m(4.7, -74.0, 4.8, -74.1) == pytest.approx(
            haversine_m(4.8, -74.1, 4.7, -74.0)
        )


class TestClustering:
    def test_agrupa_reportes_cercanos(self):
        reports = [
            r("a", 4.710989, -74.072092),
            r("b", 4.711050, -74.072100),
            r("c", 4.711010, -74.072150),
        ]
        clusters = cluster_reports(reports, radius_m=120, min_reports=3)
        assert len(clusters) == 1
        assert clusters[0]["report_count"] == 3
        assert set(clusters[0]["report_ids"]) == {"a", "b", "c"}

    def test_descarta_grupos_pequenos(self):
        reports = [r("a", 4.71, -74.07), r("b", 4.7101, -74.0701)]
        assert cluster_reports(reports, min_reports=3) == []

    def test_separa_zonas_distantes(self):
        cerca = [r(f"c{i}", 4.7100 + i * 0.00001, -74.0720) for i in range(3)]
        lejos = [r(f"l{i}", 4.7500 + i * 0.00001, -74.1000) for i in range(3)]
        clusters = cluster_reports(cerca + lejos, radius_m=120, min_reports=3)
        assert len(clusters) == 2

    def test_ordena_por_severidad_descendente(self):
        leves = [r(f"a{i}", 4.7100 + i * 0.00001, -74.0720, severity=1) for i in range(3)]
        graves = [r(f"b{i}", 4.7500 + i * 0.00001, -74.1000, severity=5) for i in range(3)]
        clusters = cluster_reports(leves + graves, min_reports=3)
        assert clusters[0]["severity_score"] > clusters[1]["severity_score"]

    def test_categoria_dominante(self):
        reports = [
            r("a", 4.7100, -74.0720, category="escombros"),
            r("b", 4.71001, -74.0720, category="escombros"),
            r("c", 4.71002, -74.0720, category="organicos"),
        ]
        cluster = cluster_reports(reports, min_reports=3)[0]
        assert cluster["dominant_category"] == "escombros"
        assert cluster["category_breakdown"] == {"escombros": 2, "organicos": 1}

    def test_centroide_dentro_del_grupo(self):
        reports = [r(f"x{i}", 4.7100 + i * 0.0001, -74.0720) for i in range(3)]
        cluster = cluster_reports(reports, radius_m=200, min_reports=3)[0]
        assert 4.7100 <= cluster["centroid"]["lat"] <= 4.7102

    def test_lista_vacia(self):
        assert cluster_reports([]) == []


def test_bounding_geohashes_incluye_celda_central():
    assert encode_geohash(4.710989, -74.072092, 6) in bounding_geohashes(4.710989, -74.072092)
