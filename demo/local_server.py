#!/usr/bin/env python3
"""Servidor de demostración local de EcoRuta.

Ejecuta **los mismos handlers de Lambda** que se despliegan en AWS, pero
sustituyendo dos cosas por dobles locales:

    DynamoDB          →  InMemoryReportRepository (el mismo que usan las pruebas)
    Autorizador JWT   →  identidad fija, configurable con ?operador=1

Todo lo demás es el código de producción: la validación de entrada, el cálculo
de geohash, el agrupamiento espacial, las transiciones de estado, los
indicadores y las cabeceras de seguridad de las respuestas.

No requiere credenciales de AWS, ni red, ni instalar nada: solo la biblioteca
estándar de Python 3.9 o superior.

    python3 demo/local_server.py
    → abrir http://localhost:8000

Advertencia: es una demostración. La autenticación está deshabilitada a
propósito, así que no debe exponerse fuera de la máquina local.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "backend"))

from src.common.repository import InMemoryReportRepository  # noqa: E402
from src.common.services import NullPublisher, ReportService  # noqa: E402
from src.handlers import (  # noqa: E402
    create_report,
    get_report,
    hotspots,
    indicators,
    update_status,
)

CIUDADANO = "demo_ciudadano_01"
OPERADOR = "demo_operador_01"

# ---------------------------------------------------------------------------
# Composición: un único servicio compartido, igual que en la Lambda real
# ---------------------------------------------------------------------------

SERVICIO = ReportService(InMemoryReportRepository(), NullPublisher())

for _modulo in (create_report, get_report, update_status, hotspots, indicators):
    _modulo.get_service = lambda: SERVICIO  # inyección del doble local


class _Contexto:
    """Sustituye al objeto `context` que AWS Lambda pasa a cada invocación."""

    aws_request_id = "demo-local"


def _evento(method: str, path_params=None, query=None, body=None, operador=False) -> dict:
    """Construye un evento de API Gateway v2 equivalente al real."""
    return {
        "body": json.dumps(body) if body is not None else None,
        "pathParameters": path_params,
        "queryStringParameters": query,
        "requestContext": {
            "http": {"method": method},
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": OPERADOR if operador else CIUDADANO,
                        "cognito:groups": "[operadores]" if operador else "[ciudadanos]",
                    }
                }
            },
        },
    }


# ---------------------------------------------------------------------------
# Datos de siembra: puntos críticos verosímiles en Bogotá
# ---------------------------------------------------------------------------

FOCOS = [
    # (nombre, lat, lon, cuántos reportes, categoría dominante, severidad base)
    ("Separador Av. NQS con Calle 63", 4.657800, -74.083500, 6, "escombros", 4),
    ("Caño detrás de la plaza de mercado", 4.598100, -74.076200, 5, "organicos", 5),
    ("Lote baldío Suba Rincón", 4.744900, -74.094300, 4, "voluminosos", 3),
    ("Andén Calle 26 con Carrera 30", 4.630500, -74.083900, 4, "reciclables", 2),
    ("Ronda quebrada Kennedy", 4.628700, -74.152400, 3, "peligrosos", 5),
]

DISPERSOS = 12  # reportes aislados que NO deben formar punto crítico


def sembrar(semilla: int = 7) -> int:
    """Carga un histórico verosímil para que la demo arranque con contenido."""
    rnd = random.Random(semilla)
    total = 0

    for _nombre, lat, lon, cuantos, categoria, sev in FOCOS:
        for i in range(cuantos):
            # Dispersión de ~40 m alrededor del foco: dentro del radio de 120 m
            payload = {
                "lat": lat + rnd.uniform(-0.00035, 0.00035),
                "lon": lon + rnd.uniform(-0.00035, 0.00035),
                # Uno de cada foco llega sin clasificar: es lo que en producción
                # resolvería la clasificación asistida sobre la fotografía.
                "category": "no_clasificado" if i == cuantos - 1 else categoria,
                "severity": max(1, min(5, sev + rnd.choice([-1, 0, 0, 1]))),
                "description": "Reporte de demostración",
            }
            SERVICIO.create(payload, CIUDADANO)
            total += 1

    for _ in range(DISPERSOS):
        SERVICIO.create(
            {
                "lat": 4.60 + rnd.uniform(0, 0.16),
                "lon": -74.18 + rnd.uniform(0, 0.13),
                "category": rnd.choice(["reciclables", "organicos", "escombros"]),
                "severity": rnd.randint(1, 3),
                "description": "Reporte aislado de demostración",
            },
            CIUDADANO,
        )
        total += 1

    # Un foco ya atendido, para mostrar que sale del análisis al cerrarse
    ids = []
    for i in range(3):
        creado = SERVICIO.create(
            {
                "lat": 4.667000 + i * 0.00002,
                "lon": -74.056000,
                "category": "escombros",
                "severity": 3,
                "description": "Foco ya intervenido",
            },
            CIUDADANO,
        )
        ids.append(creado["report_id"])
        total += 1
    for rid in ids:
        for estado in ("verificado", "programado", "atendido"):
            SERVICIO.change_status(rid, estado, OPERADOR)

    return total


# ---------------------------------------------------------------------------
# Enrutador HTTP
# ---------------------------------------------------------------------------

def _crear(_query, cuerpo, operador):
    return create_report.handler(_evento("POST", body=cuerpo, operador=operador), _Contexto())


def _puntos_criticos(query, _cuerpo, operador):
    return hotspots.handler(_evento("GET", query=query, operador=operador), _Contexto())


def _indicadores(query, _cuerpo, operador):
    return indicators.handler(_evento("GET", query=query, operador=operador), _Contexto())


RUTAS = {
    ("POST", "/reportes"): _crear,
    ("GET", "/puntos-criticos"): _puntos_criticos,
    ("GET", "/indicadores"): _indicadores,
}


class Manejador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, formato, *args):  # noqa: A002 - firma de la clase base
        sys.stderr.write("  %s\n" % (formato % args))

    # -- utilidades -------------------------------------------------------
    def _responder(self, respuesta: dict) -> None:
        cuerpo = (respuesta.get("body") or "").encode("utf-8")
        self.send_response(respuesta["statusCode"])
        for k, v in respuesta.get("headers", {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _archivo(self, ruta: Path, tipo: str) -> None:
        if not ruta.is_file():
            self.send_error(404)
            return
        datos = ruta.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def _despachar(self, metodo: str) -> None:
        partes = urllib.parse.urlparse(self.path)
        query = {k: v[0] for k, v in urllib.parse.parse_qs(partes.query).items()}
        operador = query.pop("operador", "0") == "1"

        if metodo == "GET" and partes.path in ("/", "/index.html"):
            self._archivo(Path(__file__).parent / "index.html", "text/html; charset=utf-8")
            return

        # Leaflet va incluido en el repositorio: la demostración no depende de
        # una CDN ni de tener red al momento de la sustentación.
        if metodo == "GET" and partes.path.startswith("/vendor/"):
            relativa = partes.path.lstrip("/")
            if ".." in relativa:
                self.send_error(400)
                return
            tipos = {".js": "application/javascript", ".css": "text/css", ".png": "image/png"}
            destino = Path(__file__).parent / relativa
            self._archivo(destino, tipos.get(destino.suffix, "application/octet-stream"))
            return

        cuerpo = None
        if metodo == "POST":
            largo = int(self.headers.get("Content-Length") or 0)
            crudo = self.rfile.read(largo).decode("utf-8") if largo else "{}"
            try:
                cuerpo = json.loads(crudo)
            except json.JSONDecodeError:
                cuerpo = {}

        handler = RUTAS.get((metodo, partes.path))
        if handler is None:
            self.send_error(404, "ruta no definida en la demostración")
            return
        self._responder(handler(query, cuerpo, operador))

    def do_GET(self):  # noqa: N802 - nombre impuesto por la clase base
        self._despachar("GET")

    def do_POST(self):  # noqa: N802
        self._despachar("POST")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demostración local de EcoRuta")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--sin-datos", action="store_true", help="arrancar con la base vacía")
    args = parser.parse_args()

    total = 0 if args.sin_datos else sembrar()
    kpi = SERVICIO.indicators()

    print("=" * 66)
    print("  EcoRuta · demostración local")
    print("=" * 66)
    print("  Handlers reales sobre repositorio en memoria (sin AWS)")
    print(f"  Reportes sembrados : {total}")
    print(f"  Estado             : {kpi['por_estado']}")
    print(f"  Abrir              : http://{args.host}:{args.port}")
    print("=" * 66)

    ThreadingHTTPServer((args.host, args.port), Manejador).serve_forever()


if __name__ == "__main__":
    main()
