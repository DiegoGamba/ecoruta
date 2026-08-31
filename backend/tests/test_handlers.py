"""Pruebas de los handlers con el servicio real sobre el repositorio en memoria.

Cubren el contrato HTTP completo (códigos, cabeceras, autorización) sin tocar AWS.
"""
import json

import pytest

from src.common.repository import InMemoryReportRepository
from src.common.services import NullPublisher, ReportService
from src.handlers import (
    create_report,
    get_report,
    hotspots,
    indicators,
    update_status,
)

BOGOTA = (4.710989, -74.072092)


class Ctx:
    aws_request_id = "req-test"


@pytest.fixture
def service(monkeypatch):
    svc = ReportService(InMemoryReportRepository(), NullPublisher())
    for module in (create_report, get_report, update_status, hotspots, indicators):
        monkeypatch.setattr(module, "get_service", lambda: svc)
    return svc


def event(body=None, groups="", path=None, query=None, sub="usuario_demo_1"):
    return {
        "body": json.dumps(body) if body is not None else None,
        "pathParameters": path,
        "queryStringParameters": query,
        "requestContext": {
            "authorizer": {"jwt": {"claims": {"sub": sub, "cognito:groups": groups}}}
        },
    }


def body_of(res):
    return json.loads(res["body"])


def crear(service, **over):
    payload = {"lat": BOGOTA[0], "lon": BOGOTA[1], "category": "escombros", "severity": 3}
    payload.update(over)
    return create_report.handler(event(payload), Ctx())


class TestCrearReporte:
    def test_201_con_location(self, service):
        res = crear(service)
        assert res["statusCode"] == 201
        assert res["headers"]["Location"].startswith("/reportes/")

    def test_no_expone_al_usuario(self, service):
        assert "user_id" not in body_of(crear(service))

    def test_400_por_categoria_invalida(self, service):
        res = crear(service, category="basura")
        assert res["statusCode"] == 400

    def test_400_por_coordenada_fuera_de_rango(self, service):
        assert crear(service, lat=120)["statusCode"] == 400

    def test_403_sin_identidad(self, service):
        res = create_report.handler({"body": "{}", "requestContext": {}}, Ctx())
        assert res["statusCode"] == 403

    def test_400_con_json_malformado(self, service):
        ev = event()
        ev["body"] = "{roto"
        assert create_report.handler(ev, Ctx())["statusCode"] == 400


class TestConsultarReporte:
    def test_200(self, service):
        rid = body_of(crear(service))["report_id"]
        res = get_report.handler(event(path={"id": rid}), Ctx())
        assert res["statusCode"] == 200
        assert body_of(res)["report_id"] == rid

    def test_404(self, service):
        res = get_report.handler(event(path={"id": "inexistente"}), Ctx())
        assert res["statusCode"] == 404

    def test_400_sin_id(self, service):
        assert get_report.handler(event(path=None), Ctx())["statusCode"] == 400


class TestCambiarEstado:
    def test_403_sin_grupo_operadores(self, service):
        rid = body_of(crear(service))["report_id"]
        res = update_status.handler(
            event({"status": "verificado"}, path={"id": rid}), Ctx()
        )
        assert res["statusCode"] == 403

    def test_200_con_grupo_operadores(self, service):
        rid = body_of(crear(service))["report_id"]
        res = update_status.handler(
            event({"status": "verificado"}, groups="[operadores]", path={"id": rid}),
            Ctx(),
        )
        assert res["statusCode"] == 200
        assert body_of(res)["status"] == "verificado"

    def test_400_por_transicion_invalida(self, service):
        rid = body_of(crear(service))["report_id"]
        res = update_status.handler(
            event({"status": "atendido"}, groups="[operadores]", path={"id": rid}),
            Ctx(),
        )
        assert res["statusCode"] == 400


class TestPuntosCriticos:
    def test_agrupa(self, service):
        for i in range(3):
            crear(service, lat=BOGOTA[0] + i * 0.00002)
        res = hotspots.handler(
            event(query={"lat": str(BOGOTA[0]), "lon": str(BOGOTA[1])}), Ctx()
        )
        assert res["statusCode"] == 200
        assert body_of(res)["hotspot_count"] == 1

    def test_400_sin_coordenadas(self, service):
        assert hotspots.handler(event(query={}), Ctx())["statusCode"] == 400

    def test_acota_el_radio_solicitado(self, service):
        res = hotspots.handler(
            event(query={"lat": str(BOGOTA[0]), "lon": str(BOGOTA[1]), "radius_m": "99999"}),
            Ctx(),
        )
        assert body_of(res)["params"]["radius_m"] == 1000


class TestIndicadores:
    def test_403_para_ciudadano(self, service):
        assert indicators.handler(event(), Ctx())["statusCode"] == 403

    def test_200_para_operador(self, service):
        crear(service)
        res = indicators.handler(event(groups="[operadores]"), Ctx())
        assert res["statusCode"] == 200
        assert body_of(res)["total_reportes"] == 1
