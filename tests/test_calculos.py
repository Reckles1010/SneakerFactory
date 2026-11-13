"""Cálculo: cancelados, pedido multilínea (Caso A), ticket sin duplicaciones, filtros, RFM (Caso F)."""
import pytest

from data.analiticas import build_analytics
from data.pipeline import load_synthetic


@pytest.fixture
def an(contrato):
    return build_analytics(load_synthetic(contrato))


def test_11_exclusion_de_cancelados_y_pendientes_de_ventas(an):
    k = an["kpis"]
    assert k["pedidos_actividad"] == 3 and k["pedidos_venta"] == 1          # P2 cancelado y P3 pendiente solo en actividad
    assert k["pedidos_cancelados"] == 1 and k["pedidos_pendientes"] == 1


def test_12_pedido_custom_de_40_pares_en_varias_tallas_caso_A(an):
    p1 = an["lineas_enriquecidas"].query("id_pedido == 'P1'")
    assert p1["cantidad"].sum() == 40 and p1["talla"].nunique() == 3 and len(p1) == 3
    assert an["kpis"]["pares"] == 40                                          # línea a línea = KPI
    assert an["kpis"]["ingresos"] == pytest.approx(15 * 50 + 15 * 50 + 10 * 80)


def test_13_pedido_multilinea_cuenta_como_un_pedido_y_ticket_sin_duplicar(an):
    p = an["pedidos_unicos"]
    assert len(p) == 3 and p.loc[p["id_pedido"] == "P1", "numero_lineas"].iloc[0] == 3
    assert an["kpis"]["ticket"] == pytest.approx(2300.0)                      # 2300 € / 1 pedido de venta (no / 3 líneas)


def test_14_un_cliente_con_varios_pedidos_rfm_correcto_caso_F(an):
    r = an["rfm"].set_index("id_cliente")
    assert r.loc["C1", "frequency"] == 1                                      # P2 cancelado no es compra válida
    assert r.loc["C2", "segmento_rfm"] == "Sin compras válidas"


def test_15_filtros_combinables_y_filtro_vacio_no_restringe(contrato):
    s = load_synthetic(contrato)
    sin = build_analytics(s, {"models": None, "sizes": [], "start": None})["kpis"]
    con = build_analytics(s, {"sizes": ["40"], "types": ["Custom"]})["kpis"]
    assert sin["pares"] == 40 and con["pares"] == 15
    assert build_analytics(s, {"models": ["no existe"]})["kpis"]["ingresos"] == 0


def test_16_custom_no_disponible_se_avisa(acc):
    from data.pipeline import load_and_validate
    a = build_analytics(load_and_validate(acc, escribir_salidas=False))
    assert a["custom_estandar"]["nota"].iloc[0].startswith("Custom no existe")
    assert a["margen"]["estado"].iloc[0] == "NO CALCULABLE"
