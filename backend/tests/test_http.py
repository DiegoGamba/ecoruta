import base64
import json

import pytest

from src.common.http import (
    get_groups,
    get_user_id,
    handler_wrapper,
    parse_body,
    require_group,
    response,
)
from src.common.models import ValidationError


def event(body=None, sub="usuario_demo_1", groups=""):
    return {
        "body": body,
        "requestContext": {
            "authorizer": {"jwt": {"claims": {"sub": sub, "cognito:groups": groups}}}
        },
    }


class Ctx:
    aws_request_id = "req-1"


class TestRespuesta:
    def test_incluye_cabeceras_de_seguridad(self):
        res = response(200, {"ok": True})
        assert res["headers"]["X-Content-Type-Options"] == "nosniff"
        assert res["headers"]["Cache-Control"] == "no-store"
        assert json.loads(res["body"]) == {"ok": True}


class TestCuerpo:
    def test_json_valido(self):
        assert parse_body(event('{"lat": 1}')) == {"lat": 1}

    def test_cuerpo_vacio(self):
        assert parse_body(event(None)) == {}

    def test_base64(self):
        ev = event(base64.b64encode(b'{"a":1}').decode())
        ev["isBase64Encoded"] = True
        assert parse_body(ev) == {"a": 1}

    def test_json_malformado(self):
        with pytest.raises(ValidationError):
            parse_body(event("{no-json"))

    def test_array_rechazado(self):
        with pytest.raises(ValidationError):
            parse_body(event("[1,2]"))


class TestIdentidad:
    def test_extrae_sub(self):
        assert get_user_id(event()) == "usuario_demo_1"

    def test_sin_sub(self):
        with pytest.raises(PermissionError):
            get_user_id({"requestContext": {}})

    def test_grupos(self):
        assert get_groups(event(groups="[operadores admins]")) == {"operadores", "admins"}

    def test_require_group_ok(self):
        require_group(event(groups="[operadores]"), "operadores")

    def test_require_group_denegado(self):
        with pytest.raises(PermissionError):
            require_group(event(groups="[ciudadanos]"), "operadores")


class TestWrapper:
    def test_validacion_da_400(self):
        @handler_wrapper
        def h(e, c):
            raise ValidationError("dato malo")

        res = h({}, Ctx())
        assert res["statusCode"] == 400
        assert json.loads(res["body"])["error"] == "dato malo"

    def test_permiso_da_403(self):
        @handler_wrapper
        def h(e, c):
            raise PermissionError("no")

        assert h({}, Ctx())["statusCode"] == 403

    def test_keyerror_da_404(self):
        @handler_wrapper
        def h(e, c):
            raise KeyError("x")

        assert h({}, Ctx())["statusCode"] == 404

    def test_error_interno_no_filtra_detalle(self):
        @handler_wrapper
        def h(e, c):
            raise RuntimeError("password=SECRETO")

        res = h({}, Ctx())
        assert res["statusCode"] == 500
        assert "SECRETO" not in res["body"]
