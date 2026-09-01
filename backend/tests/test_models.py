from datetime import datetime, timezone

import pytest

from src.common.models import (
    ValidationError,
    build_report,
    validate_status_transition,
)

USER = "abc123def456"
NOW = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)


def payload(**over):
    base = {"lat": 4.710989, "lon": -74.072092, "category": "escombros", "severity": 3}
    base.update(over)
    return base


class TestBuildReport:
    def test_reporte_valido(self):
        report = build_report(payload(), USER, now=NOW)
        assert report.status == "reportado"
        assert report.category == "escombros"
        assert report.geohash.startswith("d2g")  # zona de Bogotá
        assert report.created_at == report.updated_at

    def test_ttl_a_540_dias(self):
        report = build_report(payload(), USER, now=NOW)
        assert report.ttl > int(NOW.timestamp())

    def test_categoria_por_defecto(self):
        assert build_report({"lat": 4.7, "lon": -74.0}, USER).category == "no_clasificado"

    def test_normaliza_categoria(self):
        assert build_report(payload(category="  ESCOMBROS "), USER).category == "escombros"

    @pytest.mark.parametrize("bad", ["basura", "", 42])
    def test_categoria_invalida(self, bad):
        with pytest.raises(ValidationError):
            build_report(payload(category=bad), USER)

    @pytest.mark.parametrize("bad", [0, 6, -1, "alta"])
    def test_severidad_invalida(self, bad):
        with pytest.raises(ValidationError):
            build_report(payload(severity=bad), USER)

    def test_coordenada_fuera_de_rango(self):
        with pytest.raises(ValidationError):
            build_report(payload(lat=95), USER)

    def test_falta_coordenada(self):
        with pytest.raises(ValidationError, match="lat"):
            build_report({"lon": -74.0}, USER)

    def test_descripcion_muy_larga(self):
        with pytest.raises(ValidationError):
            build_report(payload(description="x" * 501), USER)

    def test_evidence_key_con_traversal(self):
        with pytest.raises(ValidationError):
            build_report(payload(evidence_key="../../secret"), USER)

    def test_usuario_invalido(self):
        with pytest.raises(ValidationError):
            build_report(payload(), "")

    def test_cuerpo_no_es_objeto(self):
        with pytest.raises(ValidationError):
            build_report(["no"], USER)  # type: ignore[arg-type]

    def test_vista_publica_oculta_al_usuario(self):
        public = build_report(payload(), USER).to_public()
        assert "user_id" not in public and "ttl" not in public

    def test_item_dynamo_tiene_claves_e_indices(self):
        item = build_report(payload(), USER).to_item()
        assert item["SK"] == "METADATA"
        assert item["PK"].startswith("REPORT#")
        assert item["GSI1PK"].startswith("GEO#")
        assert item["GSI2PK"] == "STATUS#reportado"

    def test_gsi3_solo_con_evidencia(self):
        sin = build_report(payload(), USER).to_item()
        con = build_report(payload(evidence_key="evidencias/2026/01/01/x.jpg"), USER).to_item()
        assert "GSI3PK" not in sin
        assert con["GSI3PK"].startswith("EVID#")


class TestTransiciones:
    @pytest.mark.parametrize(
        "actual,destino",
        [
            ("reportado", "verificado"),
            ("reportado", "descartado"),
            ("verificado", "programado"),
            ("programado", "atendido"),
        ],
    )
    def test_transiciones_validas(self, actual, destino):
        validate_status_transition(actual, destino)

    @pytest.mark.parametrize(
        "actual,destino",
        [
            ("reportado", "atendido"),
            ("atendido", "reportado"),
            ("descartado", "verificado"),
            ("verificado", "verificado"),
        ],
    )
    def test_transiciones_invalidas(self, actual, destino):
        with pytest.raises(ValidationError):
            validate_status_transition(actual, destino)

    def test_estado_inexistente(self):
        with pytest.raises(ValidationError):
            validate_status_transition("reportado", "cerrado")
