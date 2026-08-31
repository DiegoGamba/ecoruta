"""Pruebas de la lógica pura de clasificación y de las reglas de alerta."""
import pytest

from src.handlers.classify_evidence import map_labels_to_category
from src.handlers.notify_operator import build_message, is_urgent


def label(name, confidence=90.0):
    return {"Name": name, "Confidence": confidence}


class TestClasificacion:
    def test_mapea_escombros(self):
        categoria, _ = map_labels_to_category([label("Rubble"), label("Brick")])
        assert categoria == "escombros"

    def test_peligrosos_tiene_precedencia(self):
        categoria, _ = map_labels_to_category(
            [label("Plastic", 99.0), label("Battery", 75.0)]
        )
        assert categoria == "peligrosos"

    def test_descarta_baja_confianza(self):
        categoria, etiquetas = map_labels_to_category([label("Rubble", 40.0)])
        assert categoria == "no_clasificado"
        assert etiquetas == []

    def test_etiquetas_ordenadas_por_confianza(self):
        _, etiquetas = map_labels_to_category(
            [label("Plastic", 80.0), label("Bottle", 95.0)]
        )
        assert etiquetas == ["Bottle", "Plastic"]

    def test_sin_etiquetas(self):
        assert map_labels_to_category([]) == ("no_clasificado", [])

    def test_etiqueta_desconocida(self):
        categoria, etiquetas = map_labels_to_category([label("Cloud")])
        assert categoria == "no_clasificado"
        assert etiquetas == ["Cloud"]


class TestAlertas:
    @pytest.mark.parametrize(
        "detail",
        [
            {"category": "peligrosos", "severity": 1},
            {"category": "reciclables", "severity": 4},
            {"category": "organicos", "severity": 5},
        ],
    )
    def test_urgentes(self, detail):
        assert is_urgent(detail)

    @pytest.mark.parametrize(
        "detail",
        [{"category": "reciclables", "severity": 3}, {}, {"severity": "alta"}],
    )
    def test_no_urgentes(self, detail):
        assert not is_urgent(detail)

    def test_mensaje_contiene_identificador(self):
        msg = build_message({"report_id": "r-1", "category": "peligrosos", "severity": 5})
        assert "r-1" in msg and "peligrosos" in msg
