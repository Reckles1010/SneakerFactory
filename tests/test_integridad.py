"""Integridad: ID huérfano, duplicado, cardinalidad del merge, cantidad negativa (casos D)."""
import pandas as pd
import pytest

from data.pipeline import PipelineError, _merge_seguro, load_synthetic
from conftest import escribir_contrato


def _reglas(carpeta):
    try:
        return set(load_synthetic(carpeta)["issues"]["regla"]), None
    except PipelineError as e:
        return {i["regla"] for i in e.issues}, e


def test_07_id_huerfano_bloquea(tmp_path):
    ped = pd.DataFrame({"id_pedido": ["P1"], "fecha": ["2026-01-05"], "id_cliente": ["C99"], "estado": ["Entregado"], "tipo": ["Estándar"]})
    lin = pd.DataFrame({"id_linea": ["L1"], "id_pedido": ["P1"], "id_modelo": ["M1"], "talla": ["40"], "cantidad": [1], "precio_unitario": [50.0]})
    reglas, err = _reglas(escribir_contrato(tmp_path / "c", pedidos=ped, lineas=lin))
    assert err is not None and "03_huerfana_cliente" in reglas


def test_08_duplicado_exacto_recuperable_y_conflictivo_bloqueante(tmp_path):
    base = pd.DataFrame({"id_pedido": ["P1", "P1"], "fecha": ["2026-01-05"] * 2, "id_cliente": ["C1"] * 2, "estado": ["Entregado"] * 2, "tipo": ["Estándar"] * 2})
    lin = pd.DataFrame({"id_linea": ["L1"], "id_pedido": ["P1"], "id_modelo": ["M1"], "talla": ["40"], "cantidad": [1], "precio_unitario": [50.0]})
    s = load_synthetic(escribir_contrato(tmp_path / "a", pedidos=base, lineas=lin))
    assert "02_fila_duplicada_exacta" in set(s["issues"]["regla"]) and s["valid_rows"]["pedidos"] == 1
    conf = base.copy(); conf.loc[1, "estado"] = "Cancelado"
    reglas, err = _reglas(escribir_contrato(tmp_path / "b", pedidos=conf, lineas=lin))
    assert err is not None and "02_id_duplicado_conflictivo" in reglas


def test_09_cantidad_negativa_y_precio_invalido_se_excluyen(tmp_path):
    lin = pd.DataFrame({"id_linea": ["L1", "L2", "L3"], "id_pedido": ["P1"] * 3, "id_modelo": ["M1"] * 3, "talla": ["40"] * 3,
                        "cantidad": [-2, 1, 1], "precio_unitario": [50.0, "abc", 50.0]})
    ped = pd.DataFrame({"id_pedido": ["P1"], "fecha": ["2026-01-05"], "id_cliente": ["C1"], "estado": ["Entregado"], "tipo": ["Estándar"]})
    s = load_synthetic(escribir_contrato(tmp_path / "c", pedidos=ped, lineas=lin))
    reglas = set(s["issues"]["regla"])
    assert {"05_cantidad_nula_cero_o_negativa", "06_precio_no_numerico_o_negativo"} <= reglas
    assert s["valid_rows"]["lineas"] == 1 and s["lineas"]["cantidad"].min() > 0


def test_10_cardinalidad_merge_detecta_multiplicacion_de_filas():
    izq = pd.DataFrame({"k": ["a", "b"], "v": [1, 2]})
    der = pd.DataFrame({"k": ["a", "a", "b"], "w": [1, 2, 3]})
    with pytest.raises(Exception):                       # validate="many_to_one" rechaza la clave repetida
        _merge_seguro(izq, der, "k", "left", "many_to_one", "demo")
    with pytest.raises(PipelineError, match="sin resolver"):
        _merge_seguro(izq, pd.DataFrame({"k": ["a"], "w": [1]}), "k", "left", "many_to_one", "demo")
