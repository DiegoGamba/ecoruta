import pytest

from src.common.models import ValidationError
from src.common.repository import InMemoryReportRepository
from src.common.services import NullPublisher, ReportService, parse_float_param

BOGOTA = (4.710989, -74.072092)


@pytest.fixture
def service():
    return ReportService(InMemoryReportRepository(), NullPublisher())


def payload(**over):
    base = {"lat": BOGOTA[0], "lon": BOGOTA[1], "category": "escombros", "severity": 3}
    base.update(over)
    return base


class TestCrear:
    def test_crea_y_devuelve_sin_claves_internas(self, service):
        created = service.create(payload(), "usuario_demo_1")
        assert created["status"] == "reportado"
        assert not any(k.startswith(("PK", "SK", "GSI")) for k in created)

    def test_publica_evento(self):
        pub = NullPublisher()
        svc = ReportService(InMemoryReportRepository(), pub)
        svc.create(payload(), "usuario_demo_1")
        assert pub.sent[0][0] == "ReporteCreado"

    def test_rechaza_payload_invalido(self, service):
        with pytest.raises(ValidationError):
            service.create(payload(severity=99), "usuario_demo_1")


class TestConsultar:
    def test_get_oculta_al_usuario(self, service):
        rid = service.create(payload(), "usuario_demo_1")["report_id"]
        assert "user_id" not in service.get(rid)

    def test_get_inexistente(self, service):
        with pytest.raises(KeyError):
            service.get("no-existe")


class TestEstados:
    def test_cambia_estado(self, service):
        rid = service.create(payload(), "usuario_demo_1")["report_id"]
        assert service.change_status(rid, "verificado", "op1")["status"] == "verificado"

    def test_rechaza_salto_de_estado(self, service):
        rid = service.create(payload(), "usuario_demo_1")["report_id"]
        with pytest.raises(ValidationError):
            service.change_status(rid, "atendido", "op1")

    def test_flujo_completo(self, service):
        rid = service.create(payload(), "usuario_demo_1")["report_id"]
        for estado in ("verificado", "programado", "atendido"):
            service.change_status(rid, estado, "op1")
        assert service.get(rid)["status"] == "atendido"


class TestPuntosCriticos:
    def test_detecta_punto_critico(self, service):
        for i in range(4):
            service.create(payload(lat=BOGOTA[0] + i * 0.00002), "usuario_demo_1")
        result = service.hotspots(*BOGOTA, radius_m=120, min_reports=3)
        assert result["hotspot_count"] == 1
        assert result["hotspots"][0]["report_count"] == 4

    def test_ignora_reportes_atendidos(self, service):
        ids = [service.create(payload(lat=BOGOTA[0] + i * 0.00002), "usuario_demo_1")["report_id"]
               for i in range(3)]
        for rid in ids:
            for estado in ("verificado", "programado", "atendido"):
                service.change_status(rid, estado, "op1")
        assert service.hotspots(*BOGOTA, radius_m=120, min_reports=3)["hotspot_count"] == 0

    def test_sin_datos(self, service):
        result = service.hotspots(*BOGOTA, radius_m=120, min_reports=3)
        assert result["hotspot_count"] == 0 and result["analyzed_reports"] == 0


class TestIndicadores:
    def test_tasa_de_atencion(self, service):
        ids = [service.create(payload(), "usuario_demo_1")["report_id"] for _ in range(4)]
        for estado in ("verificado", "programado", "atendido"):
            service.change_status(ids[0], estado, "op1")
        kpi = service.indicators()
        assert kpi["total_reportes"] == 4
        assert kpi["tasa_atencion"] == 0.25
        assert kpi["pendientes"] == 3

    def test_sin_reportes_no_divide_por_cero(self, service):
        assert service.indicators()["tasa_atencion"] == 0.0


class TestParams:
    def test_convierte(self):
        assert parse_float_param({"lat": "4.7"}, "lat") == 4.7

    def test_faltante(self):
        with pytest.raises(ValidationError):
            parse_float_param({}, "lat")

    def test_no_numerico(self):
        with pytest.raises(ValidationError):
            parse_float_param({"lat": "norte"}, "lat")
