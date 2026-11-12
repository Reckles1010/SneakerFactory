"""Refresco (R1-R5): nuevo pedido, cancelación, sin cambios, CSV defectuoso, stock."""
import pytest

from data.analiticas import build_analytics
from data.pipeline import PipelineError, load_and_validate
from conftest import escribir_acc


def _ped(extra=""):
    return ("id_pedido,tipo,estado,descuento,fecha,id_linea_Linea de pedido,id_modelo_Modelo,id_trabajador_Trabajador,id_cliente_Clientes\n"
            "P1,Tienda,Entregado,f,2026-01-10,L1,M1,T1,C1\nP2,Online,Cancelado,f,2026-01-12,L2,M2,T1,C2\n"
            "P3,Online,Pendiente,f,2026-02-01,L3,M1,T1,C2\nP4,Tienda,Enviado,t,2026-02-03,L4,M2,T1,C1\n" + extra)


def test_22_R1_pedido_nuevo_suma_sin_doble_conteo(acc):
    antes = build_analytics(load_and_validate(acc, escribir_salidas=False))["kpis"]
    escribir_acc(acc, pedidos=_ped("P5,Online,Entregado,f,2026-02-10,L5,M1,T1,C2\n"),
                 lineas="\nL1,42,2,B,N,B,A,100\nL2,40,1,N,R,B,A,80\nL3,41,1,N,R,B,A,50\nL4,43,3,N,R,B,A,240\nL5,40,2,N,R,B,A,100\n")
    despues = build_analytics(load_and_validate(acc, escribir_salidas=False))["kpis"]
    assert despues["pedidos_venta"] == antes["pedidos_venta"] + 1
    assert despues["pares"] == antes["pares"] + 2 and despues["ingresos"] == pytest.approx(antes["ingresos"] + 100)


def test_23_R5_sin_cambios_misma_firma_y_mismos_kpis(acc):
    a, b = load_and_validate(acc, escribir_salidas=False), load_and_validate(acc, escribir_salidas=False)
    assert a["signature"] == b["signature"] and str(build_analytics(a)["kpis"]) == str(build_analytics(b)["kpis"])   # str: NaN != NaN


def test_24_R4_csv_defectuoso_no_publica_y_se_recupera(acc):
    ok = load_and_validate(acc, escribir_salidas=False)
    original = (acc / "Pedido.csv").read_text(encoding="utf-8")
    (acc / "Pedido.csv").write_text(original.replace("id_cliente_Clientes", "otra"), encoding="utf-8")
    with pytest.raises(PipelineError):
        load_and_validate(acc, escribir_salidas=False)
    (acc / "Pedido.csv").write_text(original, encoding="utf-8")                # recuperación
    assert load_and_validate(acc, escribir_salidas=False)["signature"] == ok["signature"]


def test_25_R3_cambio_de_stock_cambia_alertas(acc):
    a = build_analytics(load_and_validate(acc, escribir_salidas=False))["stock_cobertura"].set_index("id_modelo")
    assert a.loc["M2", "alerta"] == "Stock bajo" and a.loc["M1", "alerta"] == "Correcto"
    escribir_acc(acc, modelos="id_modelo,nombre,precio,stock,id_producto_Productos\nM1,Zapa Uno,50,3,P1\nM2,Zapa Dos,80,500,P1\n")
    b = build_analytics(load_and_validate(acc, escribir_salidas=False))["stock_cobertura"].set_index("id_modelo")
    assert b.loc["M1", "alerta"] == "Stock bajo" and b.loc["M2", "alerta"] == "Correcto"
