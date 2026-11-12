"""Reproducibilidad del generador sintético (Caso G)."""
from data.generador_datos import generar
from data.pipeline import load_synthetic


def test_17_misma_semilla_mismo_dataset(tmp_path):
    a, b = generar(7, out_dir=tmp_path / "a"), generar(7, out_dir=tmp_path / "b")
    assert a["lineas"].equals(b["lineas"]) and a["pedidos"].equals(b["pedidos"])
    assert not a["lineas"].equals(generar(8, out_dir=tmp_path / "c")["lineas"])


def test_18_dataset_sintetico_cumple_minimos(tmp_path):
    generar(42, out_dir=tmp_path / "s")
    s = load_synthetic(tmp_path / "s")
    assert s["valid_rows"]["pedidos"] >= 800 and s["valid_rows"]["lineas"] >= 1600
    assert s["valid_rows"]["clientes"] == 40 and s["valid_rows"]["modelos"] == 12 and s["lineas"]["mes"].nunique() == 18
    assert s["origin"] == "SINTÉTICO"
